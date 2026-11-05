"""drop recipe cook_time

Revision ID: 127804c19431
Revises: 071e03b4f851
Create Date: 2026-11-05 08:59:52.000000

`perform_time` is the recipe's cook time everywhere: the UI labels it "Cook Time" and every importer
maps schema.org `cookTime` into it. `cook_time` was a leftover column that nothing wrote, so exports
and the iCal feed showed an empty cook time (#7938).

Old rows can still hold a value only in `cook_time`. It moves into `perform_time` as text when the
recipe has no cook time of its own, then the column goes away.

"""

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op
from mealie.core.root_logger import get_logger

# revision identifiers, used by Alembic.
revision = "127804c19431"
down_revision: str | None = "071e03b4f851"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade():
    # "none" is what old scrapers wrote for a zero-length time; it isn't worth keeping
    result = op.get_bind().execute(
        text(
            """
            UPDATE recipes SET perform_time = cook_time
            WHERE (perform_time IS NULL OR TRIM(perform_time) = '')
              AND perform_time_seconds IS NULL
              AND cook_time IS NOT NULL
              AND TRIM(cook_time) != ''
              AND LOWER(TRIM(cook_time)) != 'none'
            """
        )
    )
    get_logger().info("Moved %s legacy recipe cook times into perform_time", result.rowcount)

    with op.batch_alter_table("recipes", schema=None) as batch_op:
        batch_op.drop_column("cook_time")


def downgrade():
    # The moved values stay in perform_time, which is where older versions read the cook time from
    with op.batch_alter_table("recipes", schema=None) as batch_op:
        batch_op.add_column(sa.Column("cook_time", sa.String(), nullable=True))
