"""Rebuild recipe search indexes with ``uv run python -m mealie.search.rebuild``."""

from mealie.db.db_setup import session_context
from mealie.search.index import rebuild


def main() -> None:
    with session_context() as session:
        rebuild(session.connection())
        session.commit()


if __name__ == "__main__":
    main()
