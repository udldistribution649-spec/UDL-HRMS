from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_roles
from app.models.department_manager_scope import DepartmentManagerScope
from app.models.department_manager_scope_request import DepartmentManagerScopeRequest
from app.models.security import UserRole, Role
from app.schemas.department_manager_scope import DepartmentManagerScopeResponse
from app.schemas.department_manager_scope_request import (
    DepartmentManagerScopeRequestCreate,
    DepartmentManagerScopeRequestResponse,
    DepartmentManagerScopeRequestDecision,
)
from app.services.department_manager_scope_request_service import (
    create_scope_request,
    decide_scope_request,
    execute_scope_request,
)

router = APIRouter(
    prefix="/department-manager-scopes",
    tags=["Department Manager Scope Workflow"],
)


@router.post(
    "/requests",
    response_model=DepartmentManagerScopeRequestResponse,
    status_code=201,
)
def submit_scope_request(
    data: DepartmentManagerScopeRequestCreate,
    current_user=Depends(require_roles("HR Admin")),
    db: Session = Depends(get_db),
):
    try:
        return create_scope_request(db, data, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/requests/{request_id}/decision/{decision}",
    response_model=DepartmentManagerScopeRequestResponse,
)
def director_decision(
    request_id: int,
    decision: str,
    data: DepartmentManagerScopeRequestDecision,
    current_user=Depends(require_roles("Director")),
    db: Session = Depends(get_db),
):
    try:
        return decide_scope_request(
            db=db,
            request_id=request_id,
            director_user_id=current_user.id,
            decision=decision.upper(),
            reason=data.reason,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/requests/{request_id}/execute",
    response_model=DepartmentManagerScopeRequestResponse,
)
def execute_approved_request(
    request_id: int,
    current_user=Depends(require_roles("Super Admin")),
    db: Session = Depends(get_db),
):
    try:
        return execute_scope_request(
            db=db,
            request_id=request_id,
            executed_by=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get(
    "/requests",
    response_model=list[DepartmentManagerScopeRequestResponse],
)
def list_scope_requests(
    current_user=Depends(require_roles("HR Admin", "Director", "Super Admin")),
    db: Session = Depends(get_db),
):
    query = db.query(DepartmentManagerScopeRequest)

    is_hr_admin = (
        db.query(UserRole)
        .join(Role, UserRole.role_id == Role.id)
        .filter(
            UserRole.user_id == current_user.id,
            Role.name == "HR Admin",
            Role.is_active == True,
        )
        .first()
    )

    is_super_admin = (
        db.query(UserRole)
        .join(Role, UserRole.role_id == Role.id)
        .filter(
            UserRole.user_id == current_user.id,
            Role.name == "Super Admin",
            Role.is_active == True,
        )
        .first()
    )

    if not is_hr_admin and not is_super_admin:
        query = query.filter(
            DepartmentManagerScopeRequest.director_user_id == current_user.id
        )

    return query.order_by(
        DepartmentManagerScopeRequest.created_at.desc()
    ).all()


@router.get(
    "/",
    response_model=list[DepartmentManagerScopeResponse],
)
def list_active_scopes(
    current_user=Depends(require_roles("Super Admin")),
    db: Session = Depends(get_db),
):
    return (
        db.query(DepartmentManagerScope)
        .filter(DepartmentManagerScope.is_active == True)
        .order_by(DepartmentManagerScope.id.desc())
        .all()
    )
