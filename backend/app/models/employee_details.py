from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmployeePersonalDetails(Base):
    __tablename__ = "employee_personal_details"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        unique=True,
        nullable=False,
    )

    gender = Column(String(20), nullable=True)
    religion = Column(String(50), nullable=True)
    religious_sect = Column(String(50), nullable=True)

    date_of_birth = Column(Date, nullable=True)
    birth_city = Column(String(100), nullable=True)

    father_or_husband_name = Column(String(150), nullable=True)
    father_or_husband_national_id_type = Column(String(30), nullable=True)
    father_or_husband_national_id_number = Column(String(30), nullable=True)

    number_of_dependents = Column(Integer, nullable=True)
    marital_status = Column(String(30), nullable=True)
    married_on = Column(Date, nullable=True)

    national_id_type = Column(String(30), nullable=True)
    national_id_number = Column(String(30), nullable=True)
    national_id_expiry_date = Column(Date, nullable=True)

    frc_number = Column(String(50), nullable=True)
    mark_of_identification = Column(Text, nullable=True)
    domicile_city = Column(String(100), nullable=True)

    ntn_number = Column(String(30), nullable=True)
    driving_license_number = Column(String(50), nullable=True)
    driving_license_expiry_date = Column(Date, nullable=True)

    employee = relationship("Employee", backref="personal_details")


class EmployeeFamilyMember(Base):
    __tablename__ = "employee_family_members"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    member_name = Column(String(150), nullable=False)
    relationship_type = Column(String(50), nullable=True)
    national_id_type = Column(String(30), nullable=True)
    national_id_number = Column(String(30), nullable=True)
    national_id_expiry_date = Column(Date, nullable=True)

    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(150), nullable=True)

    is_emergency_contact = Column(Boolean, default=False, nullable=False)

    employee = relationship("Employee", backref="family_members")