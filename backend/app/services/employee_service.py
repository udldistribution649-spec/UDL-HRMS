
from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.employee_assignment_history import EmployeeAssignmentHistory
from app.models.organization import (
    Location,
    Division,
    Department,
    SubDepartment,
    Designation,
    Grade,
    SubGrade,
)


ORG_FIELDS = {
    "location_id",
    "division_id",
    "department_id",
    "sub_department_id",
    "designation_id",
    "grade_id",
    "sub_grade_id",
    "reporting_manager_id",
}


def next_employee_code(db: Session) -> str:
    """Generate the next numeric Employee Code."""

    if db.bind.dialect.name == "postgresql":
        db.execute(
            text("SELECT pg_advisory_xact_lock(:lock_key)"),
            {"lock_key": 72419031},
        )

    last_code = (
        db.query(Employee.employee_code)
        .filter(Employee.employee_code.op("~")(r"^[0-9]+$"))
        .order_by(
            text("length(employee_code) DESC"),
            Employee.employee_code.desc(),
        )
        .with_for_update()
        .first()
    )

    if last_code is None:
        return "1"

    return str(int(last_code[0]) + 1)


def _get_active_record(db: Session, model, record_id: int, label: str):
    record = db.get(model, record_id)

    if record is None:
        raise ValueError(f"{label} does not exist.")

    if not record.is_active:
        raise ValueError(f"{label} is inactive.")

    return record


def validate_employee_refs(
    db: Session,
    values: dict,
    employee_id: int | None = None,
) -> None:
    """Validate organization references and reporting manager."""

    _get_active_record(
        db, Location, values["location_id"], "Location"
    )

    division = _get_active_record(
        db, Division, values["division_id"], "Division"
    )

    department = _get_active_record(
        db, Department, values["department_id"], "Department"
    )

    _get_active_record(
        db, Designation, values["designation_id"], "Designation"
    )

    if department.division_id != division.id:
        raise ValueError(
            "Selected Department does not belong to the selected Division."
        )

    sub_department_id = values.get("sub_department_id")

    if sub_department_id is not None:
        sub_department = _get_active_record(
            db, SubDepartment, sub_department_id, "Sub-Department"
        )

        if sub_department.department_id != department.id:
            raise ValueError(
                "Selected Sub-Department does not belong to "
                "the selected Department."
            )

    grade_id = values.get("grade_id")
    sub_grade_id = values.get("sub_grade_id")

    if sub_grade_id is not None and grade_id is None:
        raise ValueError(
            "Grade is required when Sub-Grade is selected."
        )

    grade = None

    if grade_id is not None:
        grade = _get_active_record(
            db, Grade, grade_id, "Grade"
        )

    if sub_grade_id is not None:
        sub_grade = _get_active_record(
            db, SubGrade, sub_grade_id, "Sub-Grade"
        )

        if sub_grade.grade_id != grade.id:
            raise ValueError(
                "Selected Sub-Grade does not belong to the selected Grade."
            )

    # Multiple root employees are allowed.
    reporting_manager_id = values.get("reporting_manager_id")

    if reporting_manager_id is None:
        return
    if employee_id is not None and reporting_manager_id == employee_id:
        raise ValueError(
            "Employee cannot be their own Reporting Manager."
        )

    manager = db.get(Employee, reporting_manager_id)

    if manager is None:
        raise ValueError("Reporting Manager does not exist.")

    if not manager.is_active:
        raise ValueError("Reporting Manager is inactive.")


def record_assignment(
    db: Session,
    employee: Employee,
    changed_by: int,
    reason: str,
    effective_from: date,
) -> EmployeeAssignmentHistory:
    """Save an employee's organization assignment snapshot."""

    if not reason or len(reason.strip()) < 3:
        raise ValueError(
            "Assignment reason must contain at least 3 characters."
        )

    history = EmployeeAssignmentHistory(
        employee_id=employee.id,
        location_id=employee.location_id,
        division_id=employee.division_id,
        department_id=employee.department_id,
        sub_department_id=employee.sub_department_id,
        designation_id=employee.designation_id,
        grade_id=employee.grade_id,
        sub_grade_id=employee.sub_grade_id,
        reporting_manager_id=employee.reporting_manager_id,
        effective_from=effective_from,
        changed_by=changed_by,
        reason=reason.strip(),
    )

    db.add(history)

    return history
