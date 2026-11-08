from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)

from app.core.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(150), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class Division(Base):
    __tablename__ = "divisions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(150), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class Department(Base):
    __tablename__ = "departments"
    __table_args__ = (
        UniqueConstraint(
            "division_id",
            "code",
            name="uq_departments_division_code",
        ),
    )
    id = Column(Integer, primary_key=True, index=True)
    division_id = Column(
        Integer, ForeignKey("divisions.id"), nullable=False
    )
    code = Column(String(20), nullable=False)
    name = Column(String(150), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class SubDepartment(Base):
    __tablename__ = "sub_departments"
    __table_args__ = (
        UniqueConstraint(
            "department_id",
            "code",
            name="uq_sub_departments_department_code",
        ),
    )
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(
        Integer, ForeignKey("departments.id"), nullable=False
    )
    code = Column(String(20), nullable=False)
    name = Column(String(150), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class Designation(Base):
    __tablename__ = "designations"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(150), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class GradeType(Base):
    __tablename__ = "grade_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    grade_type_id = Column(
        Integer, ForeignKey("grade_types.id"), nullable=False
    )
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class SubGrade(Base):
    __tablename__ = "sub_grades"

    id = Column(Integer, primary_key=True, index=True)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False)
    name = Column(String(100), nullable=False)
    pf_profit_category = Column(String(30), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)