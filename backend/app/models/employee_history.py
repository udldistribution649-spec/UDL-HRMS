from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmployeeReference(Base):
    __tablename__ = "employee_references"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer, ForeignKey("employees.id"), nullable=False, index=True
    )

    name = Column(String(150), nullable=False)
    company = Column(String(150), nullable=True)
    job_title = Column(String(150), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(150), nullable=True)

    employee = relationship("Employee", backref="references")


class EmployeeEmergencyContact(Base):
    __tablename__ = "employee_emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer, ForeignKey("employees.id"), nullable=False, index=True
    )

    name = Column(String(150), nullable=False)
    relationship_type = Column(String(50), nullable=True)
    national_id_type = Column(String(30), nullable=True)
    national_id_number = Column(String(30), nullable=True)
    national_id_expiry_date = Column(Date, nullable=True)

    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(150), nullable=True)

    employee = relationship("Employee", backref="emergency_contacts")


class EmployeePreviousEmployment(Base):
    __tablename__ = "employee_previous_employments"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer, ForeignKey("employees.id"), nullable=False, index=True
    )

    company = Column(String(200), nullable=False)
    company_address = Column(Text, nullable=True)
    company_city = Column(String(100), nullable=True)
    company_phone = Column(String(30), nullable=True)
    company_email = Column(String(150), nullable=True)
    company_website = Column(String(200), nullable=True)

    job_title = Column(String(150), nullable=True)
    benefits = Column(Text, nullable=True)
    reason_for_leaving = Column(Text, nullable=True)

    from_date = Column(Date, nullable=True)
    to_date = Column(Date, nullable=True)

    employee = relationship("Employee", backref="previous_employments")