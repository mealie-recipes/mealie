from datetime import datetime

from sqlalchemy import delete

from mealie.db.models.recipe.shared import RecipeShareTokenModel
from mealie.schema.recipe.recipe_share_token import RecipeShareToken

from .repository_generic import GroupRepositoryGeneric


class RepositoryRecipeShareTokens(GroupRepositoryGeneric[RecipeShareToken, RecipeShareTokenModel]):
    def delete_expired(self, current_time: datetime) -> None:
        # Tokens have no dependent rows. Bulk deletion avoids loading their full recipes
        # through the generic delete_many method's response schema.
        statement = (
            delete(self.model)
            .where(self.model.expires_at < current_time)
            .filter_by(**self._filter_builder())
            .execution_options(synchronize_session=False)
        )
        try:
            self.session.execute(statement)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
