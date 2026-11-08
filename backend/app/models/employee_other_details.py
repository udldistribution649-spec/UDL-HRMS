from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmployeeOtherDetails(Base):
    __tablename__ = "employee_other_details"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        unique=True,
        nullable=False,
    )

    medical_or_health_issues = Column(Text, nullable=True)
    hobbies_and_other_activities = Column(Text, nullable=True)

    employee = relationship("Employee", backref="other_details")