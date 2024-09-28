"""Add is_ocr_recipe column to recipes

Revision ID: 089bfa50d0ed
Revises: 188374910655
Create Date: 2022-08-05 17:07:07.389271

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "089bfa50d0ed"
down_revision = "188374910655"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    op.add_column("recipes", sa.Column("is_ocr_recipe", sa.Boolean(), default=False, nullable=True))
    op.execute("UPDATE recipes SET is_ocr_recipe = FALSE")
    #  SQLITE does not support ALTER COLUMN, so the column will stay nullable to prevent making this migration a mess
    #  The Recipe pydantic model and the SQL server use False as default value anyway for this column so Null should be a very rare sight


def downgrade():
    op.drop_column("recipes", "is_ocr_recipe")
