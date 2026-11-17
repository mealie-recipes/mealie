from datetime import datetime
from typing import NamedTuple

import sqlalchemy as sa
from pydantic import UUID4
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.recipe_embeddings import recipe_embeddings
from mealie.schema.recipe.recipe import RecipeOut


class StaleRecipe(NamedTuple):
    recipe: RecipeOut
    updated_at: datetime | None
    """The recipe's `update_at` as it was read, which is what marks its embedding as current"""


class RepositoryRecipeEmbeddings:
    """
    One group's recipe embeddings. PostgreSQL with pgvector only: check `embeddings_available` first.

    Not a `RepositoryGeneric`, since the table has no ORM model (see mealie/db/recipe_embeddings.py).
    """

    def __init__(self, session: Session, group_id: UUID4) -> None:
        self.session = session
        self.group_id = group_id

    def get_stale(self, model: str, limit: int) -> list[StaleRecipe]:
        """Recipes that are new, were edited, or were embedded with another model. Longest-waiting first."""
        # staleness follows the recipe row only, so renaming a tag or food doesn't re-embed
        # the recipes using it until they are next edited. Compare a hash of the text if that matters.
        q = (
            sa.select(RecipeModel)
            .outerjoin(recipe_embeddings, recipe_embeddings.c.recipe_id == RecipeModel.id)
            .where(
                RecipeModel.group_id == self.group_id,
                sa.or_(
                    recipe_embeddings.c.recipe_id.is_(None),
                    recipe_embeddings.c.model != model,
                    recipe_embeddings.c.recipe_updated_at.is_distinct_from(RecipeModel.update_at),
                ),
            )
            .order_by(RecipeModel.update_at)
            .limit(limit)
            .options(*RecipeOut.loader_options())
        )
        recipes = self.session.execute(q).scalars().unique().all()
        return [StaleRecipe(RecipeOut.model_validate(recipe), recipe.update_at) for recipe in recipes]

    def save(self, model: str, embeddings: list[tuple[StaleRecipe, str | None]]) -> None:
        """
        Store each recipe's vector. None stores that the recipe can't be embedded, which keeps it
        out of both the search and `get_stale` until it is edited or the model changes.
        """
        if not embeddings:
            return

        stmt = insert(recipe_embeddings).values(
            [
                {
                    "recipe_id": stale.recipe.id,
                    "group_id": self.group_id,
                    "model": model,
                    "recipe_updated_at": stale.updated_at,
                    "embedding": vector,
                }
                for stale, vector in embeddings
            ]
        )
        updated = {name: stmt.excluded[name] for name in ("group_id", "model", "recipe_updated_at", "embedding")}
        self.session.execute(stmt.on_conflict_do_update(index_elements=["recipe_id"], set_=updated))
        self.session.commit()
