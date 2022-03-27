"""Add original_text column to recipes_ingredients

Revision ID: f1a2dbee5fe9
Revises: 6b0f5f32d602
Create Date: 2022-03-27 19:30:28.545846

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "f1a2dbee5fe9"
down_revision = "6b0f5f32d602"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("recipes_ingredients", sa.Column("original_text", sa.String(), nullable=True))


def downgrade():
    op.drop_column("recipes_ingredients", "original_text")
