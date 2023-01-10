"""merge 167eb69066ad and c2e7e37d45cb

Revision ID: 74281a49e6ae
Revises: 167eb69066ad, c2e7e37d45cb
Create Date: 2023-01-10 14:25:12.206562

"""
import sqlalchemy as sa

import mealie.db.migration_types
from alembic import op

# revision identifiers, used by Alembic.
revision = "74281a49e6ae"
down_revision = ("167eb69066ad", "c2e7e37d45cb")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
