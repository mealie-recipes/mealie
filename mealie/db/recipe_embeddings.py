"""
Storage for recipe embeddings, which power semantic recipe search.

The table is created here at startup instead of by Alembic, and is not part of the ORM metadata:
it needs the pgvector extension, which SQLite and a stock PostgreSQL image don't have, so the
schema can't depend on it. It holds derived data only, so it is safe to drop at any time.
"""

from typing import NamedTuple

import sqlalchemy as sa
from sqlalchemy.orm import Session

from mealie.core.root_logger import get_logger
from mealie.db.models._model_utils.datetime import NaiveDateTime
from mealie.db.models._model_utils.guid import GUID

logger = get_logger()

EMBEDDINGS_TABLE = "recipe_embeddings"


class Vector(sa.types.UserDefinedType):
    """pgvector's type. Values are passed as its text form, e.g. "[0.1,0.2]"."""

    cache_ok = True

    def get_col_spec(self, **_) -> str:
        return "vector"


recipe_embeddings = sa.table(
    EMBEDDINGS_TABLE,
    sa.column("recipe_id", GUID()),
    sa.column("group_id", GUID()),
    sa.column("model", sa.String()),
    # The recipe's `update_at` when it was embedded; a recipe whose own differs is stale
    sa.column("recipe_updated_at", NaiveDateTime()),
    # NULL when the provider rejected the recipe's text
    sa.column("embedding", Vector()),
)


class QueryEmbedding(NamedTuple):
    """A search string embedded with `model`. Only comparable to recipes embedded with the same model."""

    model: str
    vector: str


def vector_literal(values: list[float]) -> str:
    return "[" + ",".join(map(str, values)) + "]"


def ensure_embeddings_table(session: Session) -> bool:
    """Create the embeddings table if this database can hold it. Returns whether it exists afterwards."""
    if session.get_bind().name != "postgresql":
        return False

    if not session.execute(sa.text("SELECT 1 FROM pg_available_extensions WHERE name = 'vector'")).first():
        logger.debug("pgvector is not installed; semantic recipe search is unavailable")
        return False

    try:
        session.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
        # no dimension and so no ANN index, which lets any embedding model be used. An exact
        # scan of one group's recipes is fast; add an HNSW index if a group ever holds 100k+ recipes.
        session.execute(
            sa.text(
                f"""
                CREATE TABLE IF NOT EXISTS {EMBEDDINGS_TABLE} (
                    recipe_id uuid PRIMARY KEY REFERENCES recipes(id) ON DELETE CASCADE,
                    group_id uuid NOT NULL,
                    model text NOT NULL,
                    recipe_updated_at timestamp,
                    embedding vector
                )
                """
            )
        )
        session.execute(
            sa.text(f"CREATE INDEX IF NOT EXISTS ix_{EMBEDDINGS_TABLE}_group_id ON {EMBEDDINGS_TABLE} (group_id)")
        )
        session.commit()
    except Exception:
        session.rollback()
        logger.exception("Could not set up pgvector; semantic recipe search is unavailable")
        return False

    return True


_available: bool | None = None


def embeddings_available(session: Session) -> bool:
    """Whether the embeddings table exists. It is only ever created at startup, so the answer is cached."""
    global _available
    if _available is None:
        _available = (
            session.get_bind().name == "postgresql"
            and session.execute(sa.text(f"SELECT to_regclass('{EMBEDDINGS_TABLE}')")).scalar() is not None
        )
    return _available
