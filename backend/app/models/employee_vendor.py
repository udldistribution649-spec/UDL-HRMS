from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ThirdPartyVendor(Base):
    __tablename__ = "third_party_vendors"

    id = Column(Integer, primary_key=True, index=True)

    company_name = Column(String(200), unique=True, nullable=False)
    contact_person = Column(String(150), nullable=True)
    contact_number = Column(String(30), nullable=True)
    email = Column(String(150), nullable=True)
    address = Column(Text, nullable=True)

    is_active = Column(String(20), default="Active", nullable=False)


class EmployeeVendorAssignment(Base):
    __tablename__ = "employee_vendor_assignments"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer, ForeignKey("employees.id"), nullable=False, index=True
    )
    vendor_id = Column(
        Integer, ForeignKey("third_party_vendors.id"), nullable=False
    )

    contract_start_date = Column(Date, nullable=True)
    contract_end_date = Column(Date, nullable=True)
    monthly_service_charges = Column(Numeric(14, 2), nullable=True)

    remarks = Column(Text, nullable=True)

    employee = relationship("Employee", backref="vendor_assignments")
    vendor = relationship("ThirdPartyVendor")