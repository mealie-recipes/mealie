"""postgres fuzzy search

Revision ID: b3dbb554ba53
Revises: 38514b39a824
Create Date: 2023-04-13 06:47:04.617131

"""
import sqlalchemy as sa

import mealie.db.migration_types
from alembic import op
import alembic.context as context
from mealie.core.config import get_app_settings

# revision identifiers, used by Alembic.
revision = "b3dbb554ba53"
down_revision = "38514b39a824"
branch_labels = None
depends_on = None


def get_db_type():
    return "sqlite" if "sqlite" in self.settings.DB_URL else "postgres"


def upgrade():
    dbtype = get_db_type()
    if dbtype == "postgres":
        pass
    else:
        pass


def downgrade():
    pass
