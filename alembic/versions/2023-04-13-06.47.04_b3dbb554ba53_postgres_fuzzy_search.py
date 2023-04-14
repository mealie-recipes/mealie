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
    return op.get_context().dialect.name


def setup_postgres_trigrams():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")


def remove_postgres_trigrams():
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")


def setup_sqlite_trigrams():
    op.execute("CREATE VIRTUAL TABLE IF NOT EXISTS email USING fts5(sender, title, body);")


def remove_sqlite_trigrams():
    op.execute("DROP VIRTUAL TABLE IF EXISTS email USING fts5(sender, title, body);")


def upgrade():
    if get_db_type() == "postgres":
        setup_postgres_trigrams()
    elif get_db_type() == "sqlite":
        setup_sqlite_trigrams()
    else:
        pass


def downgrade():
    if get_db_type() == "postgres":
        remove_postgres_trigrams()
    elif get_db_type() == "sqlite":
        remove_sqlite_trigrams()
    else:
        pass
