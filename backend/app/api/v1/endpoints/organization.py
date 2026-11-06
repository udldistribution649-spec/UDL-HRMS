
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.organization import (
    Location,
    Division,
    Department,
    SubDepartment,
    Designation,
    GradeType,
    Grade,
    SubGrade,
)
from app.models.department_manager_scope import DepartmentManagerScope
from app.models.security import UserRole, Role
from app.schemas import organization as schemas
from app.services.audit_service import log_action, snapshot
from app.services.organization_code_service import next_organization_code


router = APIRouter(
    prefix="/organization",
    tags=["Organization Master"],
)


# --------------------------------------------------
# Master configuration
# --------------------------------------------------

MASTERS = {
    "locations": {
        "model": Location,
        "create": schemas.LocationCreate,
        "update": schemas.LocationUpdate,
        "response": schemas.LocationResponse,
    },
    "divisions": {
        "model": Division,
        "create": schemas.DivisionCreate,
        "update": schemas.DivisionUpdate,
        "response": schemas.DivisionResponse,
    },
    "departments": {
        "model": Department,
        "create": schemas.DepartmentCreate,
        "update": schemas.DepartmentUpdate,
        "response": schemas.DepartmentResponse,
    },
    "sub-departments": {
        "model": SubDepartment,
        "create": schemas.SubDepartmentCreate,
        "update": schemas.SubDepartmentUpdate,
        "response": schemas.SubDepartmentResponse,
    },
    "designations": {
        "model": Designation,
        "create": schemas.DesignationCreate,
        "update": schemas.DesignationUpdate,
        "response": schemas.DesignationResponse,
    },
    "grade-types": {
        "model": GradeType,
        "create": schemas.GradeTypeCreate,
        "update": schemas.GradeTypeUpdate,
        "response": schemas.GradeTypeResponse,
    },
    "grades": {
        "model": Grade,
        "create": schemas.GradeCreate,
        "update": schemas.GradeUpdate,
        "response": schemas.GradeResponse,
    },
    "sub-grades": {
        "model": SubGrade,
        "create": schemas.SubGradeCreate,
        "update": schemas.SubGradeUpdate,
        "response": schemas.SubGradeResponse,
    },
}


# --------------------------------------------------
# Role helpers
# --------------------------------------------------

def get_user_roles(db: Session, user_id: int) -> set[str]:
    rows = (
        db.query(Role.name)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(
            UserRole.user_id == user_id,
            Role.is_active.is_(True),
        )
        .all()
    )

    return {row[0] for row in rows}


def require_master_admin(db: Session, user_id: int):
    roles = get_user_roles(db, user_id)

    if not roles.intersection({"Super Admin", "HR Admin"}):
        raise HTTPException(
            status_code=403,
            detail=(
                "Only Super Admin and HR Admin can manage "
                "Organization Master records."
            ),
        )


# --------------------------------------------------
# Department Manager visibility
# --------------------------------------------------

def apply_manager_scope(
    db: Session,
    query,
    resource: str,
    user_id: int,
):
    scopes = (
        db.query(DepartmentManagerScope)
        .filter(
            DepartmentManagerScope.user_id == user_id,
            DepartmentManagerScope.is_active.is_(True),
        )
        .all()
    )

    if not scopes:
        return query.filter(False)

    department_ids = {
        scope.department_id
        for scope in scopes
    }

    if resource == "departments":
        return query.filter(
            Department.id.in_(department_ids)
        )

    if resource == "divisions":
        division_ids = (
            db.query(Department.division_id)
            .filter(Department.id.in_(department_ids))
            .distinct()
        )

        return query.filter(
            Division.id.in_(division_ids)
        )

    if resource == "sub-departments":
        full_department_ids = {
            scope.department_id
            for scope in scopes
            if scope.sub_department_id is None
        }

        specific_sub_department_ids = {
            scope.sub_department_id
            for scope in scopes
            if scope.sub_department_id is not None
        }

        conditions = []

        if full_department_ids:
            conditions.append(
                SubDepartment.department_id.in_(
                    full_department_ids
                )
            )

        if specific_sub_department_ids:
            conditions.append(
                SubDepartment.id.in_(
                    specific_sub_department_ids
                )
            )

        if not conditions:
            return query.filter(False)

        from sqlalchemy import or_

        return query.filter(or_(*conditions))

    return query


# --------------------------------------------------
# Parent reference validation
# --------------------------------------------------

def validate_parent(
    db: Session,
    resource: str,
    values: dict,
):
    parent_rules = {
        "departments": ("division_id", Division),
        "sub-departments": ("department_id", Department),
        "grades": ("grade_type_id", GradeType),
        "sub-grades": ("grade_id", Grade),
    }

    rule = parent_rules.get(resource)

    if not rule:
        return

    field, parent_model = rule
    parent_id = values.get(field)

    if parent_id is None:
        return

    parent = (
        db.query(parent_model)
        .filter(
            parent_model.id == parent_id,
            parent_model.is_active.is_(True),
        )
        .first()
    )

    if not parent:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Selected {field} does not exist "
                "or is inactive."
            ),
        )


# --------------------------------------------------
# Parent-child deactivation protection
# --------------------------------------------------

def validate_deactivation(
    db: Session,
    resource: str,
    record_id: int,
):
    child_rules = {
        "divisions": (Department, Department.division_id),
        "departments": (
            SubDepartment,
            SubDepartment.department_id,
        ),
        "grade-types": (Grade, Grade.grade_type_id),
        "grades": (SubGrade, SubGrade.grade_id),
    }

    rule = child_rules.get(resource)

    if not rule:
        return

    child_model, foreign_key = rule

    active_child = (
        db.query(child_model)
        .filter(
            foreign_key == record_id,
            child_model.is_active.is_(True),
        )
        .first()
    )

    if active_child:
        raise HTTPException(
            status_code=409,
            detail=(
                "This record cannot be deactivated while "
                "active child records exist. Deactivate "
                "its child records first."
            ),
        )


# --------------------------------------------------
# Validation helper
# --------------------------------------------------

def validate_payload(schema, payload: dict) -> dict:
    try:
        validated = schema.model_validate(payload)

        return validated.model_dump(
            exclude_unset=True
        )

    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors(include_url=False),
        )


# --------------------------------------------------
# Register CRUD endpoints for all masters
# --------------------------------------------------

def register_master(resource: str, config: dict):
    model = config["model"]
    create_schema = config["create"]
    update_schema = config["update"]
    response_schema = config["response"]

    # -------------------------
    # GET active records
    # -------------------------

    def list_records(
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        query = db.query(model).filter(
            model.is_active.is_(True)
        )

        roles = get_user_roles(
            db,
            current_user.id,
        )

        if "Department Manager" in roles:
            query = apply_manager_scope(
                db,
                query,
                resource,
                current_user.id,
            )

        return query.order_by(model.id.asc()).all()

    router.add_api_route(
        f"/{resource}/",
        list_records,
        methods=["GET"],
        response_model=list[response_schema],
        name=f"list_{resource}",
    )

    # -------------------------
    # CREATE record
    # -------------------------

    def create_record(
        payload: dict = Body(...),
        reason: str | None = Query(
            default=None,
            max_length=500,
        ),
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        require_master_admin(
            db,
            current_user.id,
        )

        values = validate_payload(
            create_schema,
            payload,
        )

        validate_parent(
            db,
            resource,
            values,
        )

        # Automatically generate organization master codes.
        if resource in {
            "locations",
            "divisions",
            "departments",
            "sub-departments",
            "designations",
        }:
            parent_id = None

            if resource == "departments":
                parent_id = values["division_id"]

            elif resource == "sub-departments":
                parent_id = values["department_id"]

            values["code"] = next_organization_code(
                db=db,
                resource=resource,
                parent_id=parent_id,
            )

        record = model(**values)
        db.add(record)

        try:
            db.flush()

            log_action(
                db=db,
                actor_user_id=current_user.id,
                action="CREATE",
                entity_type=model.__name__,
                entity_id=record.id,
                new_values=snapshot(record),
                reason=reason,
            )

            db.commit()
            db.refresh(record)

            return record

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=409,
                detail=(
                    "A conflicting record already exists "
                    "or a database constraint was violated."
                ),
            )

        except Exception:
            db.rollback()
            raise

    router.add_api_route(
        f"/{resource}/",
        create_record,
        methods=["POST"],
        response_model=response_schema,
        status_code=201,
        name=f"create_{resource}",
    )

    # -------------------------
    # UPDATE record
    # -------------------------

    def update_record(
        record_id: int,
        payload: dict = Body(...),
        reason: str | None = Query(
            default=None,
            max_length=500,
        ),
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        require_master_admin(
            db,
            current_user.id,
        )

        record = (
            db.query(model)
            .filter(model.id == record_id)
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=404,
                detail="Record not found.",
            )

        values = validate_payload(
            update_schema,
            payload,
        )

        validate_parent(
            db,
            resource,
            values,
        )

        if values.get("is_active") is False:
            validate_deactivation(
                db,
                resource,
                record_id,
            )

        old_values = snapshot(record)

        for field, value in values.items():
            setattr(record, field, value)

        try:
            db.flush()

            log_action(
                db=db,
                actor_user_id=current_user.id,
                action="UPDATE",
                entity_type=model.__name__,
                entity_id=record.id,
                old_values=old_values,
                new_values=snapshot(record),
                reason=reason,
            )

            db.commit()
            db.refresh(record)

            return record

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=409,
                detail=(
                    "A conflicting record already exists "
                    "or a database constraint was violated."
                ),
            )

        except Exception:
            db.rollback()
            raise

    router.add_api_route(
        f"/{resource}/{{record_id}}",
        update_record,
        methods=["PUT"],
        response_model=response_schema,
        name=f"update_{resource}",
    )

    # -------------------------
    # DEACTIVATE record
    # -------------------------

    def deactivate_record(
        record_id: int,
        reason: str = Query(
            ...,
            min_length=1,
            max_length=500,
        ),
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        require_master_admin(
            db,
            current_user.id,
        )

        record = (
            db.query(model)
            .filter(model.id == record_id)
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=404,
                detail="Record not found.",
            )

        if not record.is_active:
            raise HTTPException(
                status_code=409,
                detail="Record is already inactive.",
            )

        validate_deactivation(
            db,
            resource,
            record_id,
        )

        old_values = snapshot(record)
        record.is_active = False

        try:
            db.flush()

            log_action(
                db=db,
                actor_user_id=current_user.id,
                action="DEACTIVATE",
                entity_type=model.__name__,
                entity_id=record.id,
                old_values=old_values,
                new_values=snapshot(record),
                reason=reason,
            )

            db.commit()
            db.refresh(record)

            return record

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=409,
                detail=(
                    "Record could not be deactivated "
                    "because of a database constraint."
                ),
            )

        except Exception:
            db.rollback()
            raise

    router.add_api_route(
        f"/{resource}/{{record_id}}/deactivate",
        deactivate_record,
        methods=["PATCH"],
        response_model=response_schema,
        name=f"deactivate_{resource}",
    )


for resource_name, master_config in MASTERS.items():
    register_master(
        resource_name,
        master_config,
    )
