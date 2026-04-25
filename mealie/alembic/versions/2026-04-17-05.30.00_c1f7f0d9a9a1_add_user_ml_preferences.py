"""add user ml preferences

Revision ID: c1f7f0d9a9a1
Revises: 4395a04f7784
Create Date: 2026-04-17 05:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types


# revision identifiers, used by Alembic.
revision = "c1f7f0d9a9a1"
down_revision: str | None = "4395a04f7784"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    op.create_table(
        "user_ml_preferences",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("created_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.Column("update_at", mealie.db.migration_types.NaiveDateTime(), nullable=True),
        sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("taste_vector", sa.JSON(), nullable=True),
        sa.Column("onboarding_tags", sa.JSON(), nullable=True),
        sa.Column("rating_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_ml_preferences_created_at"), "user_ml_preferences", ["created_at"], unique=False)
    op.create_index(op.f("ix_user_ml_preferences_user_id"), "user_ml_preferences", ["user_id"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_user_ml_preferences_user_id"), table_name="user_ml_preferences")
    op.drop_index(op.f("ix_user_ml_preferences_created_at"), table_name="user_ml_preferences")
    op.drop_table("user_ml_preferences")
