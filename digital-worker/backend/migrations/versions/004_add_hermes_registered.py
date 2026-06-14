"""Add hermes_registered column to sys_tool_config.

Revision ID: 004
Revises: 003
Create Date: 2026-06-14
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sys_tool_config", sa.Column("hermes_registered", sa.Boolean(), server_default=sa.text("0"), nullable=False, comment="是否已注册到Hermes Agent"))


def downgrade() -> None:
    op.drop_column("sys_tool_config", "hermes_registered")
