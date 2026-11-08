from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmployeeEducation(Base):
    __tablename__ = "employee_education"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    qualification_level = Column(String(100), nullable=True)
    qualification = Column(String(150), nullable=False)
    institute = Column(String(200), nullable=True)
    grade_or_division = Column(String(50), nullable=True)

    from_date = Column(Date, nullable=True)
    to_date = Column(Date, nullable=True)

    employee = relationship("Employee", backref="education_records")


class EmployeeLanguage(Base):
    __tablename__ = "employee_languages"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False,
        index=True,
    )

    language = Column(String(100), nullable=False)

    employee = relationship("Employee", backref="language_records")