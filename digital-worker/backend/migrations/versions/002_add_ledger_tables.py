"""Add ledger config tables.

Revision ID: 002
Revises: 001
Create Date: 2026-06-02
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ma_config_stage",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("stage_code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("sort_order", sa.Integer(), default=0),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "ma_config_milestone",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("stage_id", sa.Integer(), nullable=False),
        sa.Column("milestone_code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("sort_order", sa.Integer(), default=0),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("progress_pct", sa.Float(), default=0),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["stage_id"], ["ma_config_stage.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "ma_config_work_plan",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("milestone_id", sa.Integer(), nullable=False),
        sa.Column("plan_code", sa.String(50), nullable=False, unique=True),
        sa.Column("seq_no", sa.Integer(), default=0),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("time_point", sa.String(50), nullable=True),
        sa.Column("task_mode", sa.String(50), default="人工"),
        sa.Column("is_system_task", sa.Boolean(), default=False),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["milestone_id"], ["ma_config_milestone.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "ma_config_task",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("task_code", sa.String(50), nullable=False, unique=True),
        sa.Column("task_type", sa.String(50), default="MANUAL_OP"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), default=0),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("start_time", sa.DateTime(), nullable=True),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["plan_id"], ["ma_config_work_plan.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("ma_config_task")
    op.drop_table("ma_config_work_plan")
    op.drop_table("ma_config_milestone")
    op.drop_table("ma_config_stage")
