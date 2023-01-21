"""add related user to mealplan

Revision ID: 165d943c64ee
Revises: 167eb69066ad
Create Date: 2023-01-21 16:54:44.368768

"""
import sqlalchemy as sa

import mealie.db.migration_types
from alembic import op

# revision identifiers, used by Alembic.
revision = "165d943c64ee"
down_revision = "167eb69066ad"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("group_meal_plans", sa.Column("user_id", mealie.db.migration_types.GUID(), nullable=True))
    op.create_index(op.f("ix_group_meal_plans_user_id"), "group_meal_plans", ["user_id"], unique=False)
    op.create_foreign_key(None, "group_meal_plans", "users", ["user_id"], ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "group_meal_plans", type_="foreignkey")
    op.drop_index(op.f("ix_group_meal_plans_user_id"), table_name="group_meal_plans")
    op.drop_column("group_meal_plans", "user_id")
    # ### end Alembic commands ###
