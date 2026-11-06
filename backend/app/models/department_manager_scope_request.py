from datetime import datetime
from app.core.time import utcnow

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    Index,
)

from app.core.database import Base


class DepartmentManagerScopeRequest(Base):
    __tablename__ = "department_manager_scope_requests"

    id = Column(Integer, primary_key=True, index=True)

    # ASSIGN, CHANGE, REVOKE
    request_type = Column(String(20), nullable=False)

    # PENDING, APPROVED, REJECTED, EXECUTED, CANCELLED
    status = Column(String(20), default="PENDING", nullable=False)

    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    manager_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    sub_department_id = Column(Integer, ForeignKey("sub_departments.id"), nullable=True)
    existing_scope_id = Column(
        Integer,
        ForeignKey("department_manager_scopes.id"),
        nullable=True,
    )

    request_reason = Column(Text, nullable=False)

    # Optional Director approval
    requires_director_approval = Column(Boolean, default=False, nullable=False)
    director_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_reason = Column(Text, nullable=True)
    approved_at = Column(DateTime, nullable=True)

    rejection_reason = Column(Text, nullable=True)

    executed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    executed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    __table_args__ = (
        Index("ix_scope_request_manager_status", "manager_user_id", "status"),
        Index("ix_scope_request_department_status", "department_id", "status"),
    )
