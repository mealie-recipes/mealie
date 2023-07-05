"""add quantities to meal plans

Revision ID: bf3c18cd3d48
Revises: 38514b39a824
Create Date: 2023-05-29 21:52:22.575823

"""
import sqlalchemy as sa

import mealie.db.migration_types
from alembic import op

# revision identifiers, used by Alembic.
revision = "bf3c18cd3d48"
down_revision = "b3dbb554ba53"
branch_labels = None
depends_on = None


def is_postgres():
    return op.get_context().dialect.name == "postgresql"


def upgrade():
    op.add_column(
        "group_meal_plans",
        sa.Column("quantity", sa.Float, nullable=False, server_default="1"),
    )
    pass


def downgrade():
    op.drop_column("group_meal_plans", "quantity")
    pass
