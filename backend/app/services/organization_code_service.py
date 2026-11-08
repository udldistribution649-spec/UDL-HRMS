from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.organization import (
    Location,
    Division,
    Department,
    SubDepartment,
    Designation,
)


CODE_CONFIG = {
    "locations": {
        "model": Location,
        "prefix": "LOC",
        "namespace": 73101,
        "parent_field": None,
    },
    "divisions": {
        "model": Division,
        "prefix": "DIV",
        "namespace": 73102,
        "parent_field": None,
    },
    "departments": {
        "model": Department,
        "prefix": "DEP",
        "namespace": 73103,
        "parent_field": "division_id",
    },
    "sub-departments": {
        "model": SubDepartment,
        "prefix": "SUB",
        "namespace": 73104,
        "parent_field": "department_id",
    },
    "designations": {
        "model": Designation,
        "prefix": "DES",
        "namespace": 73105,
        "parent_field": None,
    },
}


def next_organization_code(
    db: Session,
    resource: str,
    parent_id: int | None = None,
) -> str:
    """
    Generate the next organization master code.

    PostgreSQL advisory transaction locks prevent duplicate
    codes during simultaneous create requests.
    """

    config = CODE_CONFIG.get(resource)

    if config is None:
        raise ValueError("Unsupported organization master.")

    model = config["model"]
    prefix = config["prefix"]
    namespace = config["namespace"]
    parent_field = config["parent_field"]

    if parent_field and parent_id is None:
        raise ValueError("Parent ID is required for this master.")

    scope_id = parent_id if parent_field else 0

    if db.bind.dialect.name == "postgresql":
        db.execute(
            text(
                "SELECT pg_advisory_xact_lock(:namespace, :scope_id)"
            ),
            {
                "namespace": namespace,
                "scope_id": scope_id,
            },
        )

    query = db.query(model.code)

    if parent_field:
        query = query.filter(
            getattr(model, parent_field) == parent_id
            )
    pattern = rf"^{prefix}-[0-9]+$"

    existing_codes = (
        query
        .filter(model.code.op("~")(pattern))
        .all()
    )

    numbers = [
        int(code[0].split("-")[1])
        for code in existing_codes
    ]

    next_number = max(numbers, default=0) + 1

    return f"{prefix}-{next_number:04d}"