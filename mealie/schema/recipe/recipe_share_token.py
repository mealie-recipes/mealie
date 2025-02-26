from datetime import UTC, datetime, timedelta

from pydantic import UUID4, ConfigDict, Field
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.schema._mealie import MealieModel

from ...db.models.recipe import RecipeIngredientModel, RecipeInstruction, RecipeModel, RecipeShareTokenModel
from .recipe import Recipe


def defaut_expires_at_time() -> datetime:
    return datetime.now(UTC) + timedelta(days=30)


class RecipeShareTokenCreate(MealieModel):
    recipe_id: UUID4
    expires_at: datetime = Field(default_factory=defaut_expires_at_time)

    @property
    def is_expired(self) -> bool:
        return self.expires_at < datetime.now(UTC)


class RecipeShareTokenSave(RecipeShareTokenCreate):
    group_id: UUID4


class RecipeShareTokenSummary(RecipeShareTokenSave):
    id: UUID4
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RecipeShareToken(RecipeShareTokenSummary):
    recipe: Recipe
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(RecipeShareTokenModel.recipe).joinedload(RecipeModel.recipe_category),
            selectinload(RecipeShareTokenModel.recipe).joinedload(RecipeModel.tags),
            selectinload(RecipeShareTokenModel.recipe).joinedload(RecipeModel.tools),
            selectinload(RecipeShareTokenModel.recipe).joinedload(RecipeModel.nutrition),
            selectinload(RecipeShareTokenModel.recipe).joinedload(RecipeModel.settings),
            selectinload(RecipeShareTokenModel.recipe).joinedload(RecipeModel.assets),
            selectinload(RecipeShareTokenModel.recipe).joinedload(RecipeModel.notes),
            selectinload(RecipeShareTokenModel.recipe).joinedload(RecipeModel.extras),
            selectinload(RecipeShareTokenModel.recipe).joinedload(RecipeModel.comments),
            selectinload(RecipeShareTokenModel.recipe)
            .joinedload(RecipeModel.recipe_instructions)
            .joinedload(RecipeInstruction.ingredient_references),
            selectinload(RecipeShareTokenModel.recipe)
            .joinedload(RecipeModel.recipe_ingredient)
            .joinedload(RecipeIngredientModel.unit),
            selectinload(RecipeShareTokenModel.recipe)
            .joinedload(RecipeModel.recipe_ingredient)
            .joinedload(RecipeIngredientModel.food),
        ]
