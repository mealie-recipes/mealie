"""add food usda metadata fields

Revision ID: a9b8c7d6e5f4
Revises: f3a1b2c9d4e5
Create Date: 2026-04-10 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a9b8c7d6e5f4"
down_revision: str | None = "f3a1b2c9d4e5"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("ingredient_foods", schema=None) as batch_op:
        batch_op.add_column(sa.Column("usda_fdc_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("usda_description", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("usda_confidence", sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table("ingredient_foods", schema=None) as batch_op:
        batch_op.drop_column("usda_confidence")
        batch_op.drop_column("usda_description")
        batch_op.drop_column("usda_fdc_id")
