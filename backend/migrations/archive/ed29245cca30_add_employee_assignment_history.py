
"""add employee assignment history

Revision ID: ed29245cca30
Revises: f57c2ae88210
Create Date: 2026-11-03 13:12:34.719052

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ed29245cca30"
down_revision: Union[str, Sequence[str], None] = "f57c2ae88210"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "employee_assignment_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("division_id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("sub_department_id", sa.Integer(), nullable=True),
        sa.Column("designation_id", sa.Integer(), nullable=False),
        sa.Column("grade_id", sa.Integer(), nullable=True),
        sa.Column("sub_grade_id", sa.Integer(), nullable=True),
        sa.Column("reporting_manager_id", sa.Integer(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("changed_by", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),

        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"]),
        sa.ForeignKeyConstraint(["division_id"], ["divisions.id"]),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.ForeignKeyConstraint(["sub_department_id"], ["sub_departments.id"]),
        sa.ForeignKeyConstraint(["designation_id"], ["designations.id"]),
        sa.ForeignKeyConstraint(["grade_id"], ["grades.id"]),
        sa.ForeignKeyConstraint(["sub_grade_id"], ["sub_grades.id"]),
        sa.ForeignKeyConstraint(["reporting_manager_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_employee_assignment_history_id",
        "employee_assignment_history",
        ["id"],
    )

    op.create_index(
        "ix_employee_assignment_history_employee_id",
        "employee_assignment_history",
        ["employee_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_employee_assignment_history_employee_id",
        table_name="employee_assignment_history",
    )
    op.drop_index(
        "ix_employee_assignment_history_id",
        table_name="employee_assignment_history",
    )
    op.drop_table("employee_assignment_history")
