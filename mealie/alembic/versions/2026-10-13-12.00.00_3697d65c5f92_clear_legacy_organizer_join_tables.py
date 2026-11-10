"""clear legacy cookbook and meal plan rule organizer join tables

Revision ID: 3697d65c5f92
Revises: a8f3b2c1d4e5
Create Date: 2026-10-13 12:00:00.000000

86054b40fd06 copied the categories, tags and tools that cookbooks and meal plan rules
were filtered by into `query_filter_string`, but never cleared the join tables it read
them from. Those leftover rows are dead data that still reference categories, tags and
tools. The tables themselves stay, only their contents go.

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "3697d65c5f92"
down_revision: str | None = "a8f3b2c1d4e5"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None

LEGACY_JOIN_TABLES = (
    "cookbooks_to_categories",
    "cookbooks_to_tags",
    "cookbooks_to_tools",
    "plan_rules_to_categories",
    "plan_rules_to_tags",
)


def upgrade() -> None:
    for table in LEGACY_JOIN_TABLES:
        op.execute(sa.text(f"DELETE FROM {table}"))


def downgrade() -> None:
    # The rows were already folded into query_filter_string by 86054b40fd06, and that is
    # what everything reads. There is nothing to restore.
    pass
