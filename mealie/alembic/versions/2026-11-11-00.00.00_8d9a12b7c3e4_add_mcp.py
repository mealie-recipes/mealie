"""Add native MCP feature state and OAuth credentials.

Revision ID: 8d9a12b7c3e4
Revises: f3a1ae61d772
"""

import sqlalchemy as sa

from alembic import op
from mealie.db.migration_types import GUID

revision = "8d9a12b7c3e4"
down_revision = "f3a1ae61d772"
branch_labels = None
depends_on = None


def _timestamps():
    return [sa.Column("created_at", sa.DateTime(), nullable=True), sa.Column("update_at", sa.DateTime(), nullable=True)]


def upgrade():
    op.create_table(
        "mcp_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_timestamps(),
    )
    op.execute("INSERT INTO mcp_settings (id, enabled) VALUES (1, false)")
    op.create_table(
        "mcp_clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.String(2048), nullable=False, unique=True),
        sa.Column("client_name", sa.String(255), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_mcp_clients_client_id", "mcp_clients", ["client_id"])
    op.create_table(
        "mcp_grants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", GUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("household_id", GUID(), sa.ForeignKey("households.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_id", sa.String(2048), nullable=False),
        sa.Column("scopes_json", sa.Text(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_mcp_grants_user_id", "mcp_grants", ["user_id"])
    op.create_table(
        "mcp_authorization_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("client_id", sa.String(2048), nullable=False),
        sa.Column("params_json", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_mcp_authorization_requests_request_hash", "mcp_authorization_requests", ["request_hash"])
    op.create_table(
        "mcp_authorization_codes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("grant_id", sa.Integer(), sa.ForeignKey("mcp_grants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_id", sa.String(2048), nullable=False),
        sa.Column("params_json", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_mcp_authorization_codes_code_hash", "mcp_authorization_codes", ["code_hash"])
    op.create_table(
        "mcp_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("grant_id", sa.Integer(), sa.ForeignKey("mcp_grants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("family_id", sa.String(64), nullable=False),
        sa.Column("kind", sa.String(8), nullable=False),
        sa.Column("scopes_json", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_mcp_tokens_token_hash", "mcp_tokens", ["token_hash"])
    op.create_index("ix_mcp_tokens_grant_id", "mcp_tokens", ["grant_id"])
    op.create_index("ix_mcp_tokens_family_id", "mcp_tokens", ["family_id"])


def downgrade():
    for name in (
        "mcp_tokens",
        "mcp_authorization_codes",
        "mcp_authorization_requests",
        "mcp_grants",
        "mcp_clients",
        "mcp_settings",
    ):
        op.drop_table(name)
