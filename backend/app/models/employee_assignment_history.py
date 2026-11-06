from datetime import datetime
from app.core.time import utcnow

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from app.core.database import Base


class EmployeeAssignmentHistory(Base):
    __tablename__ = "employee_assignment_history"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    division_id = Column(Integer, ForeignKey("divisions.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    sub_department_id = Column(
        Integer,
        ForeignKey("sub_departments.id"),
        nullable=True,
    )
    designation_id = Column(
        Integer,
        ForeignKey("designations.id"),
        nullable=False,
    )
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=True)
    sub_grade_id = Column(Integer, ForeignKey("sub_grades.id"), nullable=True)

    reporting_manager_id = Column(
    Integer,
    ForeignKey("employees.id"),
    nullable=True,
    )

    effective_from = Column(Date, nullable=False)

    changed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    reason = Column(String(500), nullable=False)

    created_at = Column(
        DateTime,
        default=utcnow,
        nullable=False,
    )