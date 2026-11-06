from datetime import datetime
from app.core.time import utcnow

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.core.database import Base
from sqlalchemy import event

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    # Employee identity
    employee_code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)

    # Employment
    contract_type = Column(String(30), nullable=False)
    employment_status = Column(String(30), nullable=False, default="Active")
    joining_date = Column(Date, nullable=False)
    confirmation_date = Column(Date, nullable=True)

    # Organization
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    division_id = Column(Integer, ForeignKey("divisions.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    sub_department_id = Column(
        Integer, ForeignKey("sub_departments.id"), nullable=True
    )
    designation_id = Column(Integer, ForeignKey("designations.id"), nullable=False)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=True)
    sub_grade_id = Column(Integer, ForeignKey("sub_grades.id"), nullable=True)

    # Direct reporting manager
    reporting_manager_id = Column(
    Integer,
    ForeignKey("employees.id"),
    nullable=True,
    )

    # Third party employment
    third_party = Column(Boolean, default=False, nullable=False)
    third_party_company = Column(String(150), nullable=True)

    # PF / EOBI / ESSI
    pf_deduction_allowed = Column(Boolean, default=False, nullable=False)

    eobi_enabled = Column(Boolean, default=False, nullable=False)
    eobi_number = Column(String(50), nullable=True)
    eobi_registration_date = Column(Date, nullable=True)

    essi_enabled = Column(Boolean, default=False, nullable=False)
    essi_number = Column(String(50), nullable=True)
    essi_registration_date = Column(Date, nullable=True)

    zakat_exemption = Column(Boolean, default=False, nullable=False)
    interest_free_pf_account = Column(Boolean, default=False, nullable=False)

    # Record control
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    reporting_manager = relationship(
        "Employee",
        remote_side="Employee.id",
        foreign_keys=[reporting_manager_id],
    )
    previous_employee_id = Column(
    	Integer,
    	ForeignKey("employees.id"),
    	nullable=True,
    	index=True,
    )
    previous_employment = relationship(
    	"Employee",
    	remote_side="Employee.id",
    	foreign_keys=[previous_employee_id],
    )
@event.listens_for(Employee, "before_insert")
@event.listens_for(Employee, "before_update")
def enforce_pf_eligibility(mapper, connection, target):
    if (target.contract_type or "").strip().lower() == "contractual":
        target.pf_deduction_allowed = False 