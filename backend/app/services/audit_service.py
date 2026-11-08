from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterable

from sqlalchemy.orm import Session

from app.models.security import AuditLog


def _json_safe(value: Any) -> Any:
    """Convert Python values into JSON-compatible values."""

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, dict):
        return {
            str(key): _json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]

    return value


def snapshot(
    obj: Any,
    fields: Iterable[str] | None = None,
) -> dict:
    """Capture selected fields from an ORM object."""

    if fields is None:
        fields = (
            column.key
            for column in obj.__table__.columns
        )

    result = {}

    for field in fields:
        if hasattr(obj, field):
            result[field] = _json_safe(getattr(obj, field))

    return result


def log_action(
    db: Session,
    actor_user_id: int | None,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    old_values: dict | None = None,
    new_values: dict | None = None,
    reason: str | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    """Create an audit log entry within the current transaction."""

    audit_entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=_json_safe(old_values) if old_values is not None else None,
        new_values=_json_safe(new_values) if new_values is not None else None,
        reason=reason,
        ip_address=ip_address,
    )

    db.add(audit_entry)

    return audit_entry