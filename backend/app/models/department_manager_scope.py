from datetime import datetime
from app.core.time import utcnow

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Index,
    text,
)

from app.core.database import Base


class DepartmentManagerScope(Base):
    __tablename__ = "department_manager_scopes"

    id = Column(Integer, primary_key=True, index=True)

    # Manager's login account
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    # Authorized Department
    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=False,
    )

    # NULL means complete Department access
    sub_department_id = Column(
        Integer,
        ForeignKey("sub_departments.id"),
        nullable=True,
    )

    # HR Admin who assigned this access
    assigned_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    reason = Column(String(500), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    assigned_at = Column(
        DateTime,
        default=utcnow,
        nullable=False,
    )

    # Prevent duplicate full Department assignments
    __table_args__ = (
        Index(
            "uq_dm_scope_full_department",
            "user_id",
            "department_id",
            unique=True,
            postgresql_where=text("sub_department_id IS NULL AND is_active = TRUE"),
        ),
        Index(
            "uq_dm_scope_sub_department",
            "user_id",
            "sub_department_id",
            unique=True,
            postgresql_where=text("sub_department_id IS NOT NULL AND is_active = TRUE"),
        ),
    )