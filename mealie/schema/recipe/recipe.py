from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from pydantic import UUID4, BaseModel, Field, validator
from pydantic.utils import GetterDict
from slugify import slugify

from mealie.core.config import get_app_dirs
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.schema._mealie import MealieModel

from .recipe_asset import RecipeAsset
from .recipe_comments import RecipeCommentOut
from .recipe_notes import RecipeNote
from .recipe_nutrition import Nutrition
from .recipe_settings import RecipeSettings
from .recipe_step import RecipeStep

app_dirs = get_app_dirs()


class RecipeTag(MealieModel):
    id: UUID4 = None
    name: str
    slug: str

    class Config:
        orm_mode = True


class RecipeCategory(RecipeTag):
    pass


class RecipeTool(RecipeTag):
    id: UUID4
    on_hand: bool = False


class CreateRecipeByUrl(BaseModel):
    url: str

    class Config:
        schema_extra = {"example": {"url": "https://myfavoriterecipes.com/recipes"}}


class CreateRecipeBulk(BaseModel):
    url: str
    categories: list[RecipeCategory] = None
    tags: list[RecipeTag] = None


class CreateRecipeByUrlBulk(BaseModel):
    imports: list[CreateRecipeBulk]


class CreateRecipe(MealieModel):
    name: str


class RecipeSummary(MealieModel):
    id: Optional[UUID4]

    user_id: UUID4 = Field(default_factory=uuid4)
    group_id: UUID4 = Field(default_factory=uuid4)

    name: Optional[str]
    slug: str = ""
    image: Optional[Any]
    recipe_yield: Optional[str]

    total_time: Optional[str] = None
    prep_time: Optional[str] = None
    cook_time: Optional[str] = None
    perform_time: Optional[str] = None

    description: Optional[str] = ""
    recipe_category: Optional[list[RecipeCategory]] = []
    tags: Optional[list[RecipeTag]] = []
    tools: list[RecipeTool] = []
    rating: Optional[int]
    org_url: Optional[str] = Field(None, alias="orgURL")

    recipe_ingredient: Optional[list[RecipeIngredient]] = []

    date_added: Optional[datetime.date]
    date_updated: Optional[datetime.datetime]

    class Config:
        orm_mode = True

    @validator("tags", always=True, pre=True, allow_reuse=True)
    def validate_tags(cats: list[Any]):  # type: ignore
        if isinstance(cats, list) and cats and isinstance(cats[0], str):
            return [RecipeTag(id=uuid4(), name=c, slug=slugify(c)) for c in cats]
        return cats

    @validator("recipe_category", always=True, pre=True, allow_reuse=True)
    def validate_categories(cats: list[Any]):  # type: ignore
        if isinstance(cats, list) and cats and isinstance(cats[0], str):
            return [RecipeCategory(id=uuid4(), name=c, slug=slugify(c)) for c in cats]
        return cats

    @validator("group_id", always=True, pre=True, allow_reuse=True)
    def validate_group_id(group_id: Any):
        if isinstance(group_id, int):
            return uuid4()
        return group_id

    @validator("user_id", always=True, pre=True, allow_reuse=True)
    def validate_user_id(user_id: Any):
        if isinstance(user_id, int):
            return uuid4()
        return user_id


class Recipe(RecipeSummary):
    recipe_ingredient: list[RecipeIngredient] = []
    recipe_instructions: Optional[list[RecipeStep]] = []
    nutrition: Optional[Nutrition]

    # Mealie Specific
    settings: Optional[RecipeSettings] = RecipeSettings()
    assets: Optional[list[RecipeAsset]] = []
    notes: Optional[list[RecipeNote]] = []
    extras: Optional[dict] = {}

    comments: Optional[list[RecipeCommentOut]] = []

    @staticmethod
    def directory_from_id(recipe_id: UUID4 | str) -> Path:
        return app_dirs.RECIPE_DATA_DIR.joinpath(str(recipe_id))

    @property
    def directory(self) -> Path:
        if not self.id:
            raise ValueError("Recipe has no ID")

        dir = app_dirs.RECIPE_DATA_DIR.joinpath(str(self.id))
        dir.mkdir(exist_ok=True, parents=True)
        return dir

    @property
    def asset_dir(self) -> Path:
        dir = self.directory.joinpath("assets")
        dir.mkdir(exist_ok=True, parents=True)
        return dir

    @property
    def image_dir(self) -> Path:
        dir = self.directory.joinpath("images")
        dir.mkdir(exist_ok=True, parents=True)
        return dir

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(cls, name_orm: RecipeModel):
            return {
                **GetterDict(name_orm),
                # "recipe_ingredient": [x.note for x in name_orm.recipe_ingredient],
                # "recipe_category": [x.name for x in name_orm.recipe_category],
                # "tags": [x.name for x in name_orm.tags],
                "extras": {x.key_name: x.value for x in name_orm.extras},
            }

    @validator("slug", always=True, pre=True, allow_reuse=True)
    def validate_slug(slug: str, values):
        if not values.get("name"):
            return slug

        return slugify(values["name"])

    @validator("recipe_ingredient", always=True, pre=True, allow_reuse=True)
    def validate_ingredients(recipe_ingredient, values):
        if not recipe_ingredient or not isinstance(recipe_ingredient, list):
            return recipe_ingredient

        if all(isinstance(elem, str) for elem in recipe_ingredient):
            return [RecipeIngredient(note=x) for x in recipe_ingredient]

        return recipe_ingredient


from mealie.schema.recipe.recipe_ingredient import RecipeIngredient

RecipeSummary.update_forward_refs()
Recipe.update_forward_refs()
