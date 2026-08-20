"""'add user login history table'

Revision ID: 20c3efd91432
Revises: 2187537c52b8
Create Date: 2026-08-16 19:18:17.370912

"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types

# revision identifiers, used by Alembic.
revision = "20c3efd91432"
down_revision: str | None = "2187537c52b8"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


# Reuse existing enum type authmethod (already exists in DB)
auth_method_enum = sa.Enum("MEALIE", "LDAP", "OIDC", name="authmethod", create_type=False)


def upgrade():
    op.create_table(
        "user_login_history",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=True),
        sa.Column("auth_method", auth_method_enum, nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.Column("created_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.Column("update_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_user_login_history_created_at"), "user_login_history", ["created_at"], unique=False)
    op.create_index(op.f("ix_user_login_history_user_id"), "user_login_history", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_login_history_success"), "user_login_history", ["success"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_user_login_history_success"), table_name="user_login_history")
    op.drop_index(op.f("ix_user_login_history_user_id"), table_name="user_login_history")
    op.drop_index(op.f("ix_user_login_history_created_at"), table_name="user_login_history")
    op.drop_table("user_login_history")
