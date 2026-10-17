"""add meal plan position

Revision ID: a136609cde0f
Revises: 27621d27c7e1
Create Date: 2026-10-17 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "a136609cde0f"
down_revision: str | None = "1e69ea7cd45e"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    with op.batch_alter_table("group_meal_plans", schema=None) as batch_op:
        batch_op.add_column(sa.Column("position", sa.Integer(), nullable=True))

    connection = op.get_bind()
    rows = connection.execute(
        sa.text(
            """
            SELECT group_meal_plans.id, users.household_id, group_meal_plans.date
            FROM group_meal_plans
            LEFT JOIN users ON users.id = group_meal_plans.user_id
            ORDER BY users.household_id, group_meal_plans.date,
                     CASE group_meal_plans.entry_type
                         WHEN 'breakfast' THEN 0 WHEN 'lunch' THEN 1 WHEN 'dinner' THEN 2
                         WHEN 'side' THEN 3 WHEN 'snack' THEN 4 WHEN 'drink' THEN 5
                         WHEN 'dessert' THEN 6 ELSE 7
                     END,
                     group_meal_plans.created_at DESC, group_meal_plans.id
            """
        )
    ).mappings()

    positions_by_day = {}
    updates = []
    for row in rows:
        day_key = (row["household_id"], row["date"])
        position = positions_by_day.get(day_key, 0)
        updates.append({"id": row["id"], "position": position})
        positions_by_day[day_key] = position + 1

    if updates:
        connection.execute(
            sa.text("UPDATE group_meal_plans SET position = :position WHERE id = :id"),
            updates,
        )

    with op.batch_alter_table("group_meal_plans", schema=None) as batch_op:
        batch_op.alter_column("position", existing_type=sa.Integer(), nullable=False)


def downgrade():
    with op.batch_alter_table("group_meal_plans", schema=None) as batch_op:
        batch_op.drop_column("position")
