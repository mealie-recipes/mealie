"""Add creation tag to group preferences

Revision ID: 0ea6eb8eaa44
Revises: ba1e4a6cfe99
Create Date: 2024-01-04 12:40:03.062671

"""
import sqlalchemy as sa

import mealie.db.migration_types
from alembic import op

# revision identifiers, used by Alembic.
revision = "0ea6eb8eaa44"
down_revision = "ba1e4a6cfe99"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("group_preferences", schema=None) as batch_op:
        batch_op.add_column(sa.Column("recipe_creation_tag", mealie.db.migration_types.GUID(), nullable=True))
        batch_op.create_foreign_key("fk_groupprefs_tags", "tags", ["recipe_creation_tag"], ["id"])


def downgrade():
    with op.batch_alter_table("group_preferences", schema=None) as batch_op:
        batch_op.drop_constraint("fk_groupprefs_tags", type_="foreignkey")
        batch_op.drop_column("recipe_creation_tag")
