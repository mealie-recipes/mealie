"""add food nutrition fields

Revision ID: f3a1b2c9d4e5
Revises: cdc93edaf73d
Create Date: 2026-04-08 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f3a1b2c9d4e5"
down_revision: str | None = "cdc93edaf73d"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("ingredient_foods", schema=None) as batch_op:
        batch_op.add_column(sa.Column("calories", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("protein_content", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("fat_content", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("carbohydrate_content", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("fiber_content", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("sugar_content", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("sodium_content", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("saturated_fat_content", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("cholesterol_content", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("trans_fat_content", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("unsaturated_fat_content", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("serving_weight_g", sa.Float(), nullable=True))


def downgrade():
    with op.batch_alter_table("ingredient_foods", schema=None) as batch_op:
        batch_op.drop_column("serving_weight_g")
        batch_op.drop_column("unsaturated_fat_content")
        batch_op.drop_column("trans_fat_content")
        batch_op.drop_column("cholesterol_content")
        batch_op.drop_column("saturated_fat_content")
        batch_op.drop_column("sodium_content")
        batch_op.drop_column("sugar_content")
        batch_op.drop_column("fiber_content")
        batch_op.drop_column("carbohydrate_content")
        batch_op.drop_column("fat_content")
        batch_op.drop_column("protein_content")
        batch_op.drop_column("calories")
