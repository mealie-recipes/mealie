from datetime import UTC, datetime

from sqlalchemy import delete

from mealie.db.db_setup import session_context
from mealie.db.models.recipe.shared import RecipeShareTokenModel


def purge_expired_tokens() -> None:
    current_time = datetime.now(UTC)

    with session_context() as session:
        stmt = delete(RecipeShareTokenModel).filter(RecipeShareTokenModel.expires_at < current_time)
        session.execute(stmt)
        session.commit()
