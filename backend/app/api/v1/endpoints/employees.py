from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.employee import Employee
from app.models.employee_assignment_history import EmployeeAssignmentHistory
from app.models.security import Role, UserRole
from app.schemas.employee import (
    EmployeeAssignmentHistoryResponse,
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.services.audit_service import log_action, snapshot
from app.services.department_manager_scope_service import (
    get_manager_department_scopes,
    is_employee_in_manager_scope,
)
from app.services.employee_service import (
    ORG_FIELDS,
    next_employee_code,
    record_assignment,
    validate_employee_refs,
)

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)

# Roles that see every employee record
FULL_ACCESS_ROLES = {"Super Admin", "HR Admin", "Director"}


def get_user_role_names(db: Session, user_id: int) -> set[str]:
    roles = (
        db.query(Role.name)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(
            UserRole.user_id == user_id,
            Role.is_active == True,
        )
        .all()
    )
    return {role[0] for role in roles}


def get_access_level(db: Session, user_id: int) -> str:
    """'full'   -> all employees
    'scoped' -> Department Manager: only authorized department/sub-department
    'self'   -> everyone else: own record only"""
    role_names = get_user_role_names(db, user_id)

    if role_names & FULL_ACCESS_ROLES:
        return "full"
    if "Department Manager" in role_names:
        return "scoped"
    return "self"



# Create Employee — Employee Code is generated automatically
@router.post("/", response_model=EmployeeResponse, status_code=201)
def create_employee(
    data: EmployeeCreate,
    request: Request,
    current_user=Depends(require_roles("Super Admin", "HR Admin")),
    db: Session = Depends(get_db),
):
    try:
        next_code = next_employee_code(db)
        values = data.model_dump()

        if values["previous_employee_id"] is not None:
            previous_employee = db.get(
                Employee,
                values["previous_employee_id"],
            )
            if previous_employee is None:
                raise ValueError(
                    "Previous Employee record does not exist."
                )

        validate_employee_refs(db, values)

        employee = Employee(
            employee_code=next_code,
            **values,
        )
        db.add(employee)
        db.flush()

        record_assignment(
            db,
            employee,
            changed_by=current_user.id,
            reason="Initial assignment",
            effective_from=employee.joining_date,
        )

        log_action(
            db,
            current_user.id,
            "CREATE",
            "employee",
            employee.id,
            new_values={
                "employee_code": employee.employee_code,
                **snapshot(employee, values.keys()),
            },
            ip_address=request.client.host if request.client else None,
        )

        db.commit()
        db.refresh(employee)
        return employee

    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Employee record conflicts with existing data.",
        )




# Update Employee — organization / manager changes keep history
@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    request: Request,
    current_user=Depends(require_roles("Super Admin", "HR Admin")),
    db: Session = Depends(get_db),
):
    employee = db.get(Employee, employee_id)

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found.",
        )

    try:
        changes = data.model_dump(exclude_unset=True)

        effective_date = changes.pop("effective_date", None) or date.today()
        reason = changes.pop("change_reason", None)

        for field, value in changes.items():
            column = Employee.__table__.c[field]

            if value is None and not column.nullable:
                raise ValueError(f"{field} cannot be empty.")

        changes = {
            field: value
            for field, value in changes.items()
            if getattr(employee, field) != value
        }

        if not changes:
            return employee

        org_changed = any(
            field in ORG_FIELDS
            for field in changes
        )

        if org_changed and not (
            reason and len(reason.strip()) >= 3
        ):
            raise ValueError(
                "change_reason is required when organization fields "
                "or the Reporting Manager change."
            )

        if org_changed:
            merged = {
                field: changes.get(
                    field,
                    getattr(employee, field),
                )
                for field in ORG_FIELDS
            }

            validate_employee_refs(
                db,
                merged,
                employee_id=employee.id,
            )

        old_values = snapshot(employee, changes.keys())

        for field, value in changes.items():
            setattr(employee, field, value)

        if org_changed:
            record_assignment(
                db,
                employee,
                current_user.id,
                reason.strip(),
                effective_date,
            )

        log_action(
            db,
            current_user.id,
            "UPDATE",
            "employee",
            employee.id,
            old_values=old_values,
            new_values=snapshot(employee, changes.keys()),
            reason=reason,
            ip_address=request.client.host if request.client else None,
        )

        db.commit()
        db.refresh(employee)
        return employee

    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Employee record conflicts with existing data.",
        )



# Employee List and Search
@router.get("/", response_model=list[EmployeeResponse])
def get_employees(
    search: str | None = Query(default=None),
    include_inactive: bool = False,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Employee)

    if not include_inactive:
        query = query.filter(Employee.is_active == True)

    level = get_access_level(db, current_user.id)

    if level == "scoped":
        scopes = get_manager_department_scopes(db, current_user.id)

        scope_conditions = []
        for scope in scopes:
            if scope.sub_department_id is None:
                scope_conditions.append(
                    Employee.department_id == scope.department_id
                )
            else:
                scope_conditions.append(
                    and_(
                        Employee.department_id == scope.department_id,
                        Employee.sub_department_id == scope.sub_department_id,
                    )
                )

        if scope_conditions:
            query = query.filter(or_(*scope_conditions))
        else:
            query = query.filter(False)

    elif level == "self":
        query = query.filter(Employee.id == current_user.employee_id)

    if search:
        query = query.filter(
            (Employee.employee_code.ilike(f"%{search}%"))
            | (Employee.name.ilike(f"%{search}%"))
        )

    return (
        query.order_by(Employee.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def _get_visible_employee(db: Session, current_user, employee_id: int) -> Employee:
    employee = db.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found.")

    level = get_access_level(db, current_user.id)

    if level == "scoped" and not is_employee_in_manager_scope(
        db, current_user.id, employee
    ):
        raise HTTPException(status_code=404, detail="Employee not found.")

    if level == "self" and employee.id != current_user.employee_id:
        raise HTTPException(status_code=404, detail="Employee not found.")

    return employee


# Single Employee Detail
@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return _get_visible_employee(db, current_user, employee_id)


# Transfer / reporting-manager history
@router.get(
    "/{employee_id}/history",
    response_model=list[EmployeeAssignmentHistoryResponse],
)
def get_employee_history(
    employee_id: int,
    current_user=Depends(
        require_roles("Super Admin", "HR Admin", "Director")
    ),
    db: Session = Depends(get_db)
):
    if not db.get(Employee, employee_id):
        raise HTTPException(status_code=404, detail="Employee not found.")

    return (
        db.query(EmployeeAssignmentHistory)
        .filter(EmployeeAssignmentHistory.employee_id == employee_id)
        .order_by(
            EmployeeAssignmentHistory.effective_from,
            EmployeeAssignmentHistory.id,
        )
        .all()
    )
