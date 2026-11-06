from datetime import datetime
from app.core.time import utcnow
from sqlalchemy.orm import Session

from app.models.department_manager_scope_request import DepartmentManagerScopeRequest
from app.models.department_manager_scope import DepartmentManagerScope
from app.models.employee import Employee
from app.models.organization import Department, SubDepartment
from app.models.security import AuditLog, User, UserRole, Role


def _has_role(db: Session, user_id: int, role_name: str) -> bool:
    return (
        db.query(UserRole)
        .join(Role, UserRole.role_id == Role.id)
        .filter(
            UserRole.user_id == user_id,
            Role.name == role_name,
            Role.is_active == True,
        )
        .first()
        is not None
    )


def create_scope_request(db: Session, data, requested_by: int):
    try:
        # Only HR Admin can submit requests
        if not _has_role(db, requested_by, "HR Admin"):
            raise ValueError("Only HR Admin can submit scope requests.")

        manager = db.query(User).filter(
            User.id == data.manager_user_id,
            User.is_active == True,
        ).first()

        if not manager:
            raise ValueError("Active manager user account not found.")

        if not _has_role(db, data.manager_user_id, "Department Manager"):
            raise ValueError("Selected user does not have Department Manager role.")

        employee = db.query(Employee).filter(
            Employee.id == manager.employee_id,
            Employee.is_active == True,
        ).first()

        if not employee:
            raise ValueError("Active employee record for manager not found.")

        department = db.query(Department).filter(
            Department.id == data.department_id,
            Department.is_active == True,
        ).first()

        if not department:
            raise ValueError("Active Department not found.")

        if data.sub_department_id is not None:
            sub_department = db.query(SubDepartment).filter(
                SubDepartment.id == data.sub_department_id,
                SubDepartment.department_id == data.department_id,
                SubDepartment.is_active == True,
            ).first()

            if not sub_department:
                raise ValueError("Invalid Sub-Department for selected Department.")

        # Validate optional Director approval
        if data.requires_director_approval:
            if data.director_user_id is None:
                raise ValueError("Select a Director when approval is required.")

            director = db.query(User).filter(
                User.id == data.director_user_id,
                User.is_active == True,
            ).first()

            if not director or not _has_role(
                db, data.director_user_id, "Director"
            ):
                raise ValueError("Selected Director account is invalid.")
        elif data.director_user_id is not None:
            raise ValueError(
                "Director must not be selected when approval is not required."
            )

        existing_scope = None

        if data.request_type == "ASSIGN":
            if data.existing_scope_id is not None:
                raise ValueError("ASSIGN request cannot contain an existing scope.")

            active_scopes = db.query(DepartmentManagerScope).filter(
                DepartmentManagerScope.user_id == data.manager_user_id,
                DepartmentManagerScope.department_id == data.department_id,
                DepartmentManagerScope.is_active == True,
            ).all()

            for scope in active_scopes:
                if scope.sub_department_id is None:
                    raise ValueError("Manager already has full Department access.")
                if data.sub_department_id is None:
                    raise ValueError(
                        "Manager already has Sub-Department scope in this Department."
                    )
                if scope.sub_department_id == data.sub_department_id:
                    raise ValueError("This scope is already assigned.")

        elif data.request_type in ("CHANGE", "REVOKE"):
            if data.existing_scope_id is None:
                raise ValueError(
                    "CHANGE and REVOKE requests require an existing scope ID."
                )

            existing_scope = db.query(DepartmentManagerScope).filter(
                DepartmentManagerScope.id == data.existing_scope_id,
                DepartmentManagerScope.user_id == data.manager_user_id,
                DepartmentManagerScope.is_active == True,
            ).first()

            if not existing_scope:
                raise ValueError("Active scope for this manager was not found.")

            if data.request_type == "REVOKE":
                if (
                    data.department_id != existing_scope.department_id
                    or data.sub_department_id != existing_scope.sub_department_id
                ):
                    raise ValueError(
                        "REVOKE target must match the existing scope."
                    )

            if data.request_type == "CHANGE":
                if (
                    data.department_id == existing_scope.department_id
                    and data.sub_department_id == existing_scope.sub_department_id
                ):
                    raise ValueError("New scope is identical to the existing scope.")

                conflicts = db.query(DepartmentManagerScope).filter(
                    DepartmentManagerScope.user_id == data.manager_user_id,
                    DepartmentManagerScope.department_id == data.department_id,
                    DepartmentManagerScope.is_active == True,
                    DepartmentManagerScope.id != existing_scope.id,
                ).all()

                for scope in conflicts:
                    if scope.sub_department_id is None:
                        raise ValueError("Manager already has full Department access.")
                    if data.sub_department_id is None:
                        raise ValueError(
                            "Manager already has Sub-Department scope in this Department."
                        )
                    if scope.sub_department_id == data.sub_department_id:
                        raise ValueError("Target scope is already assigned.")

        request_status = (
            "PENDING" if data.requires_director_approval else "APPROVED"
        )

        request = DepartmentManagerScopeRequest(
            request_type=data.request_type,
            status=request_status,
            requested_by=requested_by,
            manager_user_id=data.manager_user_id,
            department_id=data.department_id,
            sub_department_id=data.sub_department_id,
            existing_scope_id=data.existing_scope_id,
            request_reason=data.request_reason,
            requires_director_approval=data.requires_director_approval,
            director_user_id=data.director_user_id,
        )

        db.add(request)
        db.flush()

        db.add(
            AuditLog(
                actor_user_id=requested_by,
                action="DEPARTMENT_MANAGER_SCOPE_REQUESTED",
                entity_type="DepartmentManagerScopeRequest",
                entity_id=request.id,
                new_values={
                    "request_type": data.request_type,
                    "status": request_status,
                    "manager_user_id": data.manager_user_id,
                    "department_id": data.department_id,
                    "sub_department_id": data.sub_department_id,
                    "existing_scope_id": data.existing_scope_id,
                    "requires_director_approval": data.requires_director_approval,
                    "director_user_id": data.director_user_id,
                },
                reason=data.request_reason[:500],
            )
        )

        if not data.requires_director_approval:
            db.add(
                AuditLog(
                    actor_user_id=requested_by,
                    action="DEPARTMENT_MANAGER_SCOPE_REQUEST_AUTHORIZED",
                    entity_type="DepartmentManagerScopeRequest",
                    entity_id=request.id,
                    new_values={"status": "APPROVED"},
                    reason="Director approval was not required for this request.",
                )
            )

        db.commit()
        db.refresh(request)
        return request

    except Exception:
        db.rollback()
        raise

def decide_scope_request(db: Session, request_id: int, director_user_id: int,
                         decision: str, reason: str):
    try:
        if decision not in ("APPROVE", "REJECT"):
            raise ValueError("Decision must be APPROVE or REJECT.")

        if not reason or len(reason.strip()) < 3:
            raise ValueError("A valid decision reason is required.")

        request = db.query(DepartmentManagerScopeRequest).filter(
            DepartmentManagerScopeRequest.id == request_id
        ).with_for_update().first()

        if not request:
            raise ValueError("Scope request not found.")

        if request.status != "PENDING":
            raise ValueError("Only pending requests can receive a decision.")

        if not request.requires_director_approval:
            raise ValueError("Director approval is not required for this request.")

        if request.director_user_id != director_user_id:
            raise ValueError("You are not the assigned Director for this request.")

        if not _has_role(db, director_user_id, "Director"):
            raise ValueError("Active Director role is required.")

        if request.requested_by == director_user_id:
            raise ValueError("A Director cannot approve their own request.")

        old_values = {"status": request.status}

        if decision == "APPROVE":
            request.status = "APPROVED"
            request.approved_by = director_user_id
            request.approval_reason = reason.strip()
            request.approved_at = utcnow()
            action = "DEPARTMENT_MANAGER_SCOPE_REQUEST_APPROVED"
        else:
            request.status = "REJECTED"
            request.rejection_reason = reason.strip()
            action = "DEPARTMENT_MANAGER_SCOPE_REQUEST_REJECTED"

        db.add(
            AuditLog(
                actor_user_id=director_user_id,
                action=action,
                entity_type="DepartmentManagerScopeRequest",
                entity_id=request.id,
                old_values=old_values,
                new_values={"status": request.status},
                reason=reason.strip()[:500],
            )
        )

        db.commit()
        db.refresh(request)
        return request

    except Exception:
        db.rollback()
        raise

def execute_scope_request(db: Session, request_id: int, executed_by: int):
    try:
        if not _has_role(db, executed_by, "Super Admin"):
            raise ValueError("Only Super Admin can execute scope requests.")

        request = (
            db.query(DepartmentManagerScopeRequest)
            .filter(DepartmentManagerScopeRequest.id == request_id)
            .with_for_update()
            .first()
        )

        if not request:
            raise ValueError("Scope request not found.")

        if request.request_type not in ("ASSIGN", "CHANGE", "REVOKE"):
            raise ValueError("Invalid scope request type.")

        if request.status != "APPROVED":
            raise ValueError("Only approved requests can be executed.")

        if request.requires_director_approval and not request.approved_by:
            raise ValueError("Required Director approval is missing.")

        manager = db.query(User).filter(
            User.id == request.manager_user_id,
            User.is_active == True,
        ).first()

        if not manager or not _has_role(
            db, request.manager_user_id, "Department Manager"
        ):
            raise ValueError("Active Department Manager account not found.")

        department = db.query(Department).filter(
            Department.id == request.department_id,
            Department.is_active == True,
        ).first()

        if not department:
            raise ValueError("Target Department is no longer active.")

        if request.sub_department_id is not None:
            sub_department = db.query(SubDepartment).filter(
                SubDepartment.id == request.sub_department_id,
                SubDepartment.department_id == request.department_id,
                SubDepartment.is_active == True,
            ).first()

            if not sub_department:
                raise ValueError("Target Sub-Department is no longer valid.")

        old_values = None
        existing_scope = None

        if request.request_type in ("CHANGE", "REVOKE"):
            existing_scope = (
                db.query(DepartmentManagerScope)
                .filter(
                    DepartmentManagerScope.id == request.existing_scope_id,
                    DepartmentManagerScope.user_id == request.manager_user_id,
                    DepartmentManagerScope.is_active == True,
                )
                .with_for_update()
                .first()
            )

            if not existing_scope:
                raise ValueError("Existing active scope not found.")

            old_values = {
                "scope_id": existing_scope.id,
                "department_id": existing_scope.department_id,
                "sub_department_id": existing_scope.sub_department_id,
                "is_active": True,
            }

        if request.request_type in ("ASSIGN", "CHANGE"):
            conflicts = db.query(DepartmentManagerScope).filter(
                DepartmentManagerScope.user_id == request.manager_user_id,
                DepartmentManagerScope.department_id == request.department_id,
                DepartmentManagerScope.is_active == True,
            ).all()

            for scope in conflicts:
                if existing_scope and scope.id == existing_scope.id:
                    continue

                if scope.sub_department_id is None:
                    raise ValueError("Manager already has full Department access.")

                if request.sub_department_id is None:
                    raise ValueError(
                        "Manager already has Sub-Department scope in this Department."
                    )

                if scope.sub_department_id == request.sub_department_id:
                    raise ValueError("Target scope is already assigned.")

        if request.request_type in ("CHANGE", "REVOKE"):
            existing_scope.is_active = False

        new_scope = None

        if request.request_type in ("ASSIGN", "CHANGE"):
            new_scope = DepartmentManagerScope(
                user_id=request.manager_user_id,
                department_id=request.department_id,
                sub_department_id=request.sub_department_id,
                assigned_by=executed_by,
                reason=request.request_reason[:500],
                is_active=True,
            )
            db.add(new_scope)
            db.flush()

        request.status = "EXECUTED"
        request.executed_by = executed_by
        request.executed_at = utcnow()

        db.add(
            AuditLog(
                actor_user_id=executed_by,
                action="DEPARTMENT_MANAGER_SCOPE_REQUEST_EXECUTED",
                entity_type="DepartmentManagerScopeRequest",
                entity_id=request.id,
                old_values=old_values,
                new_values={
                    "status": "EXECUTED",
                    "request_type": request.request_type,
                    "new_scope_id": new_scope.id if new_scope else None,
                    "department_id": request.department_id,
                    "sub_department_id": request.sub_department_id,
                    "old_scope_deactivated": existing_scope.id
                    if existing_scope else None,
                },
                reason="Approved scope request executed.",
            )
        )

        db.commit()
        db.refresh(request)
        return request

    except Exception:
        db.rollback()
        raise


