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
    op.execute("SET pg_trgm.word_similarity_threshold = 0.7;")
    # text <% text
    op.create_index(
        "ix_recipe_name_gin",
        table_name="recipe",
        columns=["name"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={
            "name": "gin_trgm_ops",
        },
    )
    op.create_index(
        "ix_recipe_description_gin",
        table_name="recipe",
        columns=["description"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={
            "description": "gin_trgm_ops",
        },
    )
    op.create_index(
        "ix_recipe_ingredients_note_gin",
        table_name="recipe_instructions",
        columns=["note"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={
            "note": "gin_trgm_ops",
        },
    )
    op.create_index(
        "ix_recipe_ingredients_description_gin",
        table_name="recipe_instructions",
        columns=["original_text"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={
            "original_text": "gin_trgm_ops",
        },
    )


def remove_postgres_trigrams():
    op.drop_index("ix_recipe_name_gin", table_name="recipe")
    op.drop_index("ix_recipe_description_gin", table_name="recipe")
    op.drop_index("ix_recipe_ingredients_note_gin", table_name="recipe_instructions")
    op.drop_index("ix_recipe_ingredients_description_gin", table_name="recipe_instructions")


def setup_sqlite_trigrams():
    pass


def remove_sqlite_trigrams():
    pass


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
