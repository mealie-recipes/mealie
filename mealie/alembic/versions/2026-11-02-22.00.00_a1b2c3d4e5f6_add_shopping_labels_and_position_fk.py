"""'add shopping labels and position fk'

Revision ID: a1b2c3d4e5f6
Revises: 071e03b4f851
Create Date: 2026-11-02 22:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

from mealie.db.models._model_utils.guid import GUID

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision: str | None = "071e03b4f851"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def generate_id() -> str:
    val = GUID.generate()
    dialect = op.get_bind().dialect

    return GUID.convert_value_to_guid(val, dialect)  # type: ignore


def upgrade():
    # 1. Create shopping_label table
    op.create_table(
        "shopping_labels",
        sa.Column("id", GUID(), primary_key=True, default=GUID.generate),
        sa.Column("household_id", GUID(), sa.ForeignKey("households.id"), nullable=False, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("color", sa.String(7), nullable=False, server_default="#E58325"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("household_id", "name", name="uq_shopping_label_household_name"),
    )

    # 2. Add shopping_label_id column to shopping_list_items (if not exists)
    # and create FK to shopping_labels
    with op.batch_alter_table("shopping_list_items") as batch_op:
        batch_op.add_column(sa.Column("shopping_label_id", GUID(), nullable=True))
        batch_op.create_foreign_key(
            "fk_shopping_item_shopping_label_id",
            "shopping_labels",
            ["shopping_label_id"],
            ["id"],
            ondelete="SET NULL",
        )

    # 3. Ensure position has index for ordering (already exists on position, but add composite index)
    op.create_index("ix_shopping_item_list_position", "shopping_list_items", ["shopping_list_id", "position"])


def downgrade():
    op.drop_index("ix_shopping_item_list_position", table_name="shopping_list_items")
    with op.batch_alter_table("shopping_list_items") as batch_op:
        batch_op.drop_constraint("fk_shopping_item_shopping_label_id", type_="foreignkey")
        batch_op.drop_column("shopping_label_id")
    op.drop_table("shopping_labels")
