from datetime import UTC, datetime

from mealie.db.db_setup import session_context
from mealie.repos.all_repositories import get_repositories


def purge_expired_tokens() -> None:
    current_time = datetime.now(UTC)

    with session_context() as session:
        db = get_repositories(session, group_id=None)
        db.recipe_share_tokens.delete_expired(current_time)
