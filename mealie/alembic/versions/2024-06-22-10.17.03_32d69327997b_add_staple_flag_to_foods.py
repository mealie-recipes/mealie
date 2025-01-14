"""Add staple flag to foods

Revision ID: 32d69327997b
Revises: 7788478a0338
Create Date: 2024-06-22 10:17:03.323966

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm

# revision identifiers, used by Alembic.
revision = "32d69327997b"
down_revision = "7788478a0338"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def is_postgres():
    return op.get_context().dialect.name == "postgresql"


def upgrade():
    with op.batch_alter_table("ingredient_foods") as batch_op:
        batch_op.add_column(sa.Column("on_hand", sa.Boolean(), nullable=True, default=False))

    bind = op.get_bind()
    session = orm.Session(bind=bind)

    with session:
        if is_postgres():
            stmt = "UPDATE ingredient_foods SET on_hand = FALSE;"
        else:
            stmt = "UPDATE ingredient_foods SET on_hand = 0;"

        session.execute(sa.text(stmt))

    # forbid nulls after migration
    with op.batch_alter_table("ingredient_foods") as batch_op:
        batch_op.alter_column("on_hand", nullable=False)


def downgrade():
    with op.batch_alter_table("ingredient_foods") as batch_op:
        batch_op.drop_column("on_hand")
