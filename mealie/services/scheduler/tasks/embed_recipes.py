import sqlalchemy as sa

from mealie.core.root_logger import get_logger
from mealie.db.db_setup import session_context
from mealie.db.models.group.ai_providers import AIProviderSettings
from mealie.db.recipe_embeddings import embeddings_available
from mealie.repos.all_repositories import get_repositories
from mealie.services.recipe.recipe_embedding_service import RecipeEmbeddingService

logger = get_logger()


def embed_recipes() -> None:
    """Embed new and edited recipes for every group that has an embedding provider."""
    with session_context() as session:
        if not embeddings_available(session):
            return

        group_ids = (
            session.execute(
                sa.select(AIProviderSettings.group_id).where(AIProviderSettings.embedding_provider_id.is_not(None))
            )
            .scalars()
            .all()
        )

        for group_id in group_ids:
            repos = get_repositories(session, group_id=group_id, household_id=None)
            try:
                count = RecipeEmbeddingService(repos).sync()
            except Exception:
                # Left stale, so the next run retries them
                session.rollback()
                logger.exception(f"Could not embed recipes for group {group_id}")
                continue

            if count:
                logger.info(f"Embedded {count} recipes for group {group_id}")
