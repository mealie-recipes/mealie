"""postgres fuzzy search

Revision ID: b3dbb554ba53
Revises: 38514b39a824
Create Date: 2023-04-13 06:47:04.617131

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "b3dbb554ba53"
down_revision = "38514b39a824"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def get_db_type():
    return op.get_context().dialect.name


def setup_postgres_trigrams():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.create_index(
        "ix_recipes_name_normalized_gin",
        table_name="recipes",
        columns=["name_normalized"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={
            "name_normalized": "gin_trgm_ops",
        },
    )
    op.create_index(
        "ix_recipes_description_normalized_gin",
        table_name="recipes",
        columns=["description_normalized"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={
            "description_normalized": "gin_trgm_ops",
        },
    )
    op.create_index(
        "ix_recipes_ingredients_note_normalized_gin",
        table_name="recipes_ingredients",
        columns=["note_normalized"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={
            "note_normalized": "gin_trgm_ops",
        },
    )
    op.create_index(
        "ix_recipes_ingredients_original_text_normalized_gin",
        table_name="recipes_ingredients",
        columns=["original_text_normalized"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={
            "original_text_normalized": "gin_trgm_ops",
        },
    )


def remove_postgres_trigrams():
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")
    op.drop_index("ix_recipes_name_normalized_gin", table_name="recipe")
    op.drop_index("ix_recipes_description_normalized_gin", table_name="recipe")
    op.drop_index("ix_recipes_ingredients_note_normalized_gin", table_name="recipes_ingredients")
    op.drop_index("ix_recipes_ingredients_original_text_normalized_gin", table_name="recipes_ingredients")


def upgrade():
    if get_db_type() == "postgresql":
        setup_postgres_trigrams()
    else:
        pass


def downgrade():
    if get_db_type() == "postgres":
        remove_postgres_trigrams()
    else:
        pass
