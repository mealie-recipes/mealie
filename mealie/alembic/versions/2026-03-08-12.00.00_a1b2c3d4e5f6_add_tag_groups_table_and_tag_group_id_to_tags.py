"""Add tag_groups table and tag_group_id to tags

Revision ID: a1b2c3d4e5f6
Revises: 1d9a002d7234
Create Date: 2026-03-08 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

import mealie.db.migration_types

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision: str | None = "1d9a002d7234"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    # Create tag_groups table
    op.create_table(
        "tag_groups",
        sa.Column("id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("group_id", mealie.db.migration_types.GUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("color", sa.String(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], name="fk_tag_groups_group_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", "group_id", name="tag_groups_slug_group_id_key"),
    )
    with op.batch_alter_table("tag_groups", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_tag_groups_group_id"), ["group_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_tag_groups_name"), ["name"], unique=False)
        batch_op.create_index(batch_op.f("ix_tag_groups_slug"), ["slug"], unique=False)

    # Add tag_group_id column to tags table
    with op.batch_alter_table("tags", schema=None) as batch_op:
        batch_op.add_column(sa.Column("tag_group_id", mealie.db.migration_types.GUID(), nullable=True))
        batch_op.create_index(batch_op.f("ix_tags_tag_group_id"), ["tag_group_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_tags_tag_group_id",
            "tag_groups",
            ["tag_group_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade():
    # Remove tag_group_id from tags
    with op.batch_alter_table("tags", schema=None) as batch_op:
        batch_op.drop_constraint("fk_tags_tag_group_id", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_tags_tag_group_id"))
        batch_op.drop_column("tag_group_id")

    # Drop tag_groups table
    with op.batch_alter_table("tag_groups", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_tag_groups_slug"))
        batch_op.drop_index(batch_op.f("ix_tag_groups_name"))
        batch_op.drop_index(batch_op.f("ix_tag_groups_group_id"))

    op.drop_table("tag_groups")
