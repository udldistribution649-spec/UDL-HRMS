from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmployeeContact(Base):
    __tablename__ = "employee_contacts"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        unique=True,
        nullable=False,
    )

    present_address = Column(Text, nullable=True)
    permanent_address = Column(Text, nullable=True)
    phone = Column(String(30), nullable=True)
    mobile = Column(String(30), nullable=True)
    fax = Column(String(30), nullable=True)
    email = Column(String(150), nullable=True)

    employee = relationship("Employee", backref="contact_details")


class EmployeeBankAccount(Base):
    __tablename__ = "employee_bank_accounts"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    bank = Column(String(100), nullable=False)
    branch = Column(String(150), nullable=True)
    account_number = Column(String(50), nullable=False)
    account_title = Column(String(150), nullable=True)

    employee = relationship("Employee", backref="bank_accounts")