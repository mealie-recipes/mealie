"""empty migration to fix food flag data

Revision ID: d7b3ce6fa31a
Revises: 7cf3054cbbcc
Create Date: 2025-07-11 20:17:10.543280

"""

from textwrap import dedent

from alembic import op


# revision identifiers, used by Alembic.
revision = "d7b3ce6fa31a"
down_revision: str | None = "7cf3054cbbcc"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def is_postgres():
    return op.get_context().dialect.name == "postgresql"


def upgrade():
    # Update recipes with disable_amount=True: set ingredient quantities of 1 to 0
    op.execute(
        dedent(
            f"""
                UPDATE recipes_ingredients
                SET quantity = 0
                WHERE quantity = 1
                AND recipe_id IN (
                    SELECT r.id
                    FROM recipes r
                    JOIN recipe_settings rs ON r.id = rs.recipe_id
                    WHERE rs.disable_amount = {"true" if is_postgres() else "1"}
                )
            """
        )
    )


def downgrade():
    pass
