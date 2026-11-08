from sqlalchemy.orm import Session

from app.models.department_manager_scope import DepartmentManagerScope
from app.models.employee import Employee


def get_manager_department_scopes(db: Session, user_id: int):
    return (
        db.query(DepartmentManagerScope)
        .filter(
            DepartmentManagerScope.user_id == user_id,
            DepartmentManagerScope.is_active == True,
        )
        .all()
    )


def is_employee_in_manager_scope(
    db: Session,
    user_id: int,
    employee: Employee,
) -> bool:
    scopes = get_manager_department_scopes(db, user_id)

    for scope in scopes:
        if scope.department_id != employee.department_id:
            continue

        if scope.sub_department_id is None:
            return True

        if scope.sub_department_id == employee.sub_department_id:
            return True

    return False
