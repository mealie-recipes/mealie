from datetime import UTC, datetime

from mealie.db.db_setup import session_context
from mealie.repos.all_repositories import get_repositories
from mealie.schema.response.pagination import PaginationQuery


def purge_expired_tokens() -> None:
    current_time = datetime.now(UTC)

    with session_context() as session:
        db = get_repositories(session, group_id=None)
        tokens_response = db.recipe_share_tokens.page_all(
            PaginationQuery(page=1, per_page=-1, query_filter=f"expiresAt < {current_time}")
        )
        if not (tokens := tokens_response.items):
            return

        db.recipe_share_tokens.delete_many([token.id for token in tokens])
