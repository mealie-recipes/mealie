from datetime import datetime, timedelta

from pydantic import UUID4, Field

from mealie.schema._mealie import MealieModel

from .recipe import Recipe


def defaut_expires_at_time() -> datetime:
    return datetime.utcnow() + timedelta(days=30)


class RecipeShareTokenCreate(MealieModel):
    recipe_id: UUID4
    expires_at: datetime = Field(default_factory=defaut_expires_at_time)


class RecipeShareTokenSave(RecipeShareTokenCreate):
    group_id: UUID4


class RecipeShareTokenSummary(RecipeShareTokenSave):
    id: UUID4
    created_at: datetime

    class Config:
        orm_mode = True


class RecipeShareToken(RecipeShareTokenSummary):
    recipe: Recipe

    class Config:
        orm_mode = True
