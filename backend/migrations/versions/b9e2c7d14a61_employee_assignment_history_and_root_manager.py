
"""Allow NULL reporting managers for root employees and assignment history.

Revision ID: b9e2c7d14a61
Revises: ed29245cca30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b9e2c7d14a61"
down_revision: Union[str, Sequence[str], None] = "ed29245cca30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Root employees may have no reporting manager.
    op.alter_column(
        "employees",
        "reporting_manager_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    # Assignment history must also support root employees.
    # The table was already created by ed29245cca30.
    op.alter_column(
        "employee_assignment_history",
        "reporting_manager_id",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    connection = op.get_bind()

    employee_null_count = connection.execute(
        sa.text(
            "SELECT COUNT(*) FROM employees "
            "WHERE reporting_manager_id IS NULL"
        )
    ).scalar_one()

    history_null_count = connection.execute(
        sa.text(
            "SELECT COUNT(*) FROM employee_assignment_history "
            "WHERE reporting_manager_id IS NULL"
        )
    ).scalar_one()

    if employee_null_count or history_null_count:
        raise RuntimeError(
            "Cannot downgrade: NULL reporting managers exist in "
            "employees or employee_assignment_history."
        )

    op.alter_column(
        "employee_assignment_history",
        "reporting_manager_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.alter_column(
        "employees",
        "reporting_manager_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
