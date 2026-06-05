"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "submissions",
        sa.Column("id", sa.String(length=48), nullable=False),
        sa.Column("handle", sa.String(length=64), nullable=False),
        sa.Column("mode", sa.String(length=16), nullable=False),
        sa.Column("preset", sa.String(length=32), nullable=False),
        sa.Column("files", sa.Text(), nullable=False),
        sa.Column("build_cmd", sa.Text(), nullable=True),
        sa.Column("run_cmd", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("fail_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_submissions")),
    )
    op.create_table(
        "results",
        sa.Column("submission_id", sa.String(length=48), nullable=False),
        sa.Column("length", sa.Integer(), nullable=False),
        sa.Column("runtime_ms", sa.Integer(), nullable=False),
        sa.Column("tour", sa.Text(), nullable=False),
        sa.Column("gen_log", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["submission_id"], ["submissions.id"],
                                name=op.f("fk_results_submission_id_submissions")),
        sa.PrimaryKeyConstraint("submission_id", name=op.f("pk_results")),
    )


def downgrade() -> None:
    op.drop_table("results")
    op.drop_table("submissions")
