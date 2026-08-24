"""more aggresive normalization

Revision ID: c7427796f7b6
Revises: 4395a04f7784
Create Date: 2026-05-10 18:44:53.159775

"""

from sqlalchemy import orm, text

from alembic import op
from mealie.db.models._model_base import SqlAlchemyBase


# revision identifiers, used by Alembic.
revision = "c7427796f7b6"
down_revision: str | None = "4395a04f7784"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def _update_table(session: orm.Session, table: str, columns: list[str], source_columns: list[str]) -> None:
    """Re-normalize all rows in `table`, reading raw values from `source_columns` and writing to `columns`."""
    rows = session.execute(text(f"SELECT id, {', '.join(source_columns)} FROM {table}")).fetchall()
    for row in rows:
        id_ = row[0]
        updates = {}
        for col, src in zip(columns, source_columns, strict=True):
            val = row[source_columns.index(src) + 1]
            updates[col] = SqlAlchemyBase.normalize(val) if val is not None else None

        set_clause = ", ".join(f"{col} = :{col}" for col in columns)
        session.execute(text(f"UPDATE {table} SET {set_clause} WHERE id = :id"), {**updates, "id": id_})
    session.commit()


def update_normalization() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    # recipes: name_normalized, description_normalized
    _update_table(session, "recipes", ["name_normalized", "description_normalized"], ["name", "description"])

    # recipe ingredients: note_normalized, original_text_normalized
    _update_table(
        session,
        "recipes_ingredients",
        ["note_normalized", "original_text_normalized"],
        ["note", "original_text"],
    )

    # ingredient units: name, plural_name, abbreviation, plural_abbreviation
    _update_table(
        session,
        "ingredient_units",
        ["name_normalized", "plural_name_normalized", "abbreviation_normalized", "plural_abbreviation_normalized"],
        ["name", "plural_name", "abbreviation", "plural_abbreviation"],
    )

    # ingredient foods: name, plural_name
    _update_table(session, "ingredient_foods", ["name_normalized", "plural_name_normalized"], ["name", "plural_name"])

    # unit aliases
    _update_table(session, "ingredient_units_aliases", ["name_normalized"], ["name"])

    # food aliases
    _update_table(session, "ingredient_foods_aliases", ["name_normalized"], ["name"])


def upgrade():
    # no table changes, this is a data migration
    update_normalization()


def downgrade():
    pass
