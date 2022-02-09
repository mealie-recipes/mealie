from datetime import datetime, timedelta

from fastapi_camelcase import CamelModel
from pydantic import UUID4, Field

from .recipe import Recipe


def defaut_expires_at_time() -> datetime:
    return datetime.utcnow() + timedelta(days=30)


class RecipeShareTokenCreate(CamelModel):
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
