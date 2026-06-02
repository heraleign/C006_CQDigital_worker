"""Initial database migration - creates all 36 tables.

Revision ID: 001
Revises:
Create Date: 2025-03-15
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Audit Module (8 tables)
    op.create_table(
        "dq_audit_field_config",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("field_name", sa.String(200), nullable=False),
        sa.Column("field_desc", sa.String(500), nullable=True),
        sa.Column("datasource_id", sa.String(100), nullable=True),
        sa.Column("datasource_name", sa.String(200), nullable=True),
        sa.Column("schema_name", sa.String(200), nullable=True),
        sa.Column("table_name", sa.String(200), nullable=True),
        sa.Column("field_type", sa.String(100), nullable=True),
        sa.Column("field_length", sa.Integer(), nullable=True),
        sa.Column("is_nullable", sa.Boolean(), default=True),
        sa.Column("default_value", sa.String(500), nullable=True),
        sa.Column("sample_data", sa.Text(), nullable=True),
        sa.Column("status", sa.Integer(), default=1),
        sa.Column("remark", sa.String(500), nullable=True),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "dq_audit_rule_config",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rule_name", sa.String(200), nullable=False),
        sa.Column("rule_code", sa.String(100), nullable=True, unique=True),
        sa.Column("rule_type", sa.String(50), nullable=True),
        sa.Column("rule_level", sa.String(20), nullable=True),
        sa.Column("rule_content", sa.JSON(), nullable=True),
        sa.Column("field_id", sa.Integer(), nullable=True),
        sa.Column("field_name", sa.String(200), nullable=True),
        sa.Column("table_name", sa.String(200), nullable=True),
        sa.Column("threshold", sa.Float(), nullable=True),
        sa.Column("severity", sa.String(20), default="medium"),
        sa.Column("status", sa.Integer(), default=1),
        sa.Column("ai_generated", sa.Boolean(), default=False),
        sa.Column("generate_task_id", sa.String(100), nullable=True),
        sa.Column("confirm_status", sa.String(20), default="pending"),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["field_id"], ["dq_audit_field_config.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "dq_audit_task_config",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("task_name", sa.String(200), nullable=False),
        sa.Column("task_type", sa.String(50), nullable=True),
        sa.Column("rule_ids", sa.JSON(), nullable=True),
        sa.Column("field_ids", sa.JSON(), nullable=True),
        sa.Column("schedule_type", sa.String(20), default="manual"),
        sa.Column("schedule_config", sa.JSON(), nullable=True),
        sa.Column("execute_strategy", sa.String(50), nullable=True),
        sa.Column("sample_rate", sa.Float(), default=100.0),
        sa.Column("status", sa.Integer(), default=1),
        sa.Column("importance", sa.Integer(), default=1),
        sa.Column("last_execute_time", sa.DateTime(), nullable=True),
        sa.Column("last_execute_result", sa.String(20), nullable=True),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "dq_task_importance_config",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("level_name", sa.String(100), nullable=True),
        sa.Column("color", sa.String(20), nullable=True),
        sa.Column("score_range", sa.String(100), nullable=True),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("notify_channels", sa.JSON(), nullable=True),
        sa.Column("response_time_minutes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "dq_alert_upgrade_rule",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rule_name", sa.String(200), nullable=False),
        sa.Column("alert_type", sa.String(50), nullable=True),
        sa.Column("trigger_condition", sa.JSON(), nullable=True),
        sa.Column("upgrade_level", sa.Integer(), nullable=True),
        sa.Column("notify_targets", sa.JSON(), nullable=True),
        sa.Column("notify_template", sa.Text(), nullable=True),
        sa.Column("max_upgrade_count", sa.Integer(), default=3),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "dq_audit_execution",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=True),
        sa.Column("task_name", sa.String(200), nullable=True),
        sa.Column("execute_time", sa.DateTime(), nullable=True),
        sa.Column("execute_duration", sa.Float(), nullable=True),
        sa.Column("total_records", sa.Integer(), nullable=True),
        sa.Column("sample_records", sa.Integer(), nullable=True),
        sa.Column("passed_records", sa.Integer(), nullable=True),
        sa.Column("failed_records", sa.Integer(), nullable=True),
        sa.Column("pass_rate", sa.Float(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("result_summary", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["task_id"], ["dq_audit_task_config.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "dq_audit_exception",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("execution_id", sa.Integer(), nullable=True),
        sa.Column("rule_id", sa.Integer(), nullable=True),
        sa.Column("rule_name", sa.String(200), nullable=True),
        sa.Column("field_name", sa.String(200), nullable=True),
        sa.Column("table_name", sa.String(200), nullable=True),
        sa.Column("exception_type", sa.String(50), nullable=True),
        sa.Column("exception_value", sa.Text(), nullable=True),
        sa.Column("exception_count", sa.Integer(), nullable=True),
        sa.Column("exception_rate", sa.Float(), nullable=True),
        sa.Column("severity", sa.String(20), default="medium"),
        sa.Column("status", sa.String(20), default="open"),
        sa.Column("handler", sa.String(100), nullable=True),
        sa.Column("handle_time", sa.DateTime(), nullable=True),
        sa.Column("handle_result", sa.Text(), nullable=True),
        sa.Column("alert_level", sa.String(20), nullable=True),
        sa.Column("is_upgraded", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["execution_id"], ["dq_audit_execution.id"]),
        sa.ForeignKeyConstraint(["rule_id"], ["dq_audit_rule_config.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "dq_audit_report",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("report_name", sa.String(200), nullable=False),
        sa.Column("report_type", sa.String(50), nullable=True),
        sa.Column("execution_ids", sa.JSON(), nullable=True),
        sa.Column("total_executions", sa.Integer(), nullable=True),
        sa.Column("total_records", sa.Integer(), nullable=True),
        sa.Column("total_exceptions", sa.Integer(), nullable=True),
        sa.Column("overall_pass_rate", sa.Float(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("conclusion", sa.Text(), nullable=True),
        sa.Column("recommendations", sa.JSON(), nullable=True),
        sa.Column("report_data", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(20), default="draft"),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("dq_audit_report")
    op.drop_table("dq_audit_exception")
    op.drop_table("dq_audit_execution")
    op.drop_table("dq_alert_upgrade_rule")
    op.drop_table("dq_task_importance_config")
    op.drop_table("dq_audit_task_config")
    op.drop_table("dq_audit_rule_config")
    op.drop_table("dq_audit_field_config")
