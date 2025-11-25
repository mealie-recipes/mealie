"""add_tesco_fields_to_ingredient_food

Revision ID: add_tesco_fields_to_food
Revises: 
Create Date: 2025-11-25 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_tesco_fields_to_food'
down_revision = '6887d088fc51'

def upgrade():
    op.add_column('ingredient_foods', sa.Column('tesco_product_id', sa.String(), nullable=True))
    op.add_column('ingredient_foods', sa.Column('tesco_product_url', sa.String(), nullable=True))
    op.add_column('ingredient_foods', sa.Column('tesco_price', sa.Float(), nullable=True))
    op.add_column('ingredient_foods', sa.Column('tesco_unit_price', sa.Float(), nullable=True))
    op.add_column('ingredient_foods', sa.Column('tesco_units', sa.String(), nullable=True))
    op.add_column('ingredient_foods', sa.Column('tesco_quantity', sa.Float(), nullable=True))


def downgrade():
    op.drop_column('ingredient_foods', 'tesco_quantity')
    op.drop_column('ingredient_foods', 'tesco_units')
    op.drop_column('ingredient_foods', 'tesco_unit_price')
    op.drop_column('ingredient_foods', 'tesco_price')
    op.drop_column('ingredient_foods', 'tesco_product_url')
    op.drop_column('ingredient_foods', 'tesco_product_id')
