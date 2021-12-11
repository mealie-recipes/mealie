import datetime
from pathlib import Path
from typing import Any, Optional
from uuid import UUID, uuid4

from fastapi_camelcase import CamelModel
from pydantic import BaseModel, Field, validator
from pydantic.utils import GetterDict
from slugify import slugify

from mealie.core.config import get_app_dirs
from mealie.db.models.recipe.recipe import RecipeModel

from .recipe_asset import RecipeAsset
from .recipe_comments import RecipeCommentOut
from .recipe_ingredient import RecipeIngredient
from .recipe_notes import RecipeNote
from .recipe_nutrition import Nutrition
from .recipe_settings import RecipeSettings
from .recipe_step import RecipeStep

app_dirs = get_app_dirs()


class RecipeTag(CamelModel):
    id: int
    name: str
    slug: str

    class Config:
        orm_mode = True


class RecipeCategory(RecipeTag):
    pass


class RecipeTool(RecipeTag):
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


class CreateRecipe(CamelModel):
    name: str


class RecipeSummary(CamelModel):
    id: Optional[int]

    user_id: int = 0
    group_id: UUID = Field(default_factory=uuid4)

    name: Optional[str]
    slug: str = ""
    image: Optional[Any]
    recipe_yield: Optional[str]

    total_time: Optional[str] = None
    prep_time: Optional[str] = None
    cook_time: Optional[str] = None
    perform_time: Optional[str] = None

    description: Optional[str] = ""
    recipe_category: Optional[list[RecipeTag]] = []
    tags: Optional[list[RecipeTag]] = []
    tools: list[RecipeTool] = []
    rating: Optional[int]
    org_url: Optional[str] = Field(None, alias="orgURL")

    recipe_ingredient: Optional[list[RecipeIngredient]] = []

    date_added: Optional[datetime.date]
    date_updated: Optional[datetime.datetime]

    class Config:
        orm_mode = True

    @validator("tags", always=True, pre=True)
    def validate_tags(cats: list[Any]):
        if isinstance(cats, list) and cats and isinstance(cats[0], str):
            return [RecipeTag(name=c, slug=slugify(c)) for c in cats]
        return cats

    @validator("recipe_category", always=True, pre=True)
    def validate_categories(cats: list[Any]):
        if isinstance(cats, list) and cats and isinstance(cats[0], str):
            return [RecipeCategory(name=c, slug=slugify(c)) for c in cats]
        return cats

    @validator("group_id", always=True, pre=True)
    def validate_group_id(group_id: list[Any]):
        if isinstance(group_id, int):
            return uuid4()
        return group_id


class Recipe(RecipeSummary):
    recipe_ingredient: Optional[list[RecipeIngredient]] = []
    recipe_instructions: Optional[list[RecipeStep]] = []
    nutrition: Optional[Nutrition]

    # Mealie Specific
    settings: Optional[RecipeSettings] = RecipeSettings()
    assets: Optional[list[RecipeAsset]] = []
    notes: Optional[list[RecipeNote]] = []
    extras: Optional[dict] = {}

    comments: Optional[list[RecipeCommentOut]] = []

    @staticmethod
    def directory_from_slug(slug) -> Path:
        return app_dirs.RECIPE_DATA_DIR.joinpath(slug)

    @property
    def directory(self) -> Path:
        dir = app_dirs.RECIPE_DATA_DIR.joinpath(self.slug)
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
        def getter_dict(_cls, name_orm: RecipeModel):
            return {
                **GetterDict(name_orm),
                # "recipe_ingredient": [x.note for x in name_orm.recipe_ingredient],
                # "recipe_category": [x.name for x in name_orm.recipe_category],
                # "tags": [x.name for x in name_orm.tags],
                "extras": {x.key_name: x.value for x in name_orm.extras},
            }

    @validator("slug", always=True, pre=True)
    def validate_slug(slug: str, values):
        if not values.get("name"):
            return slug

        return slugify(values["name"])

    @validator("recipe_ingredient", always=True, pre=True)
    def validate_ingredients(recipe_ingredient, values):
        if not recipe_ingredient or not isinstance(recipe_ingredient, list):
            return recipe_ingredient

        if all(isinstance(elem, str) for elem in recipe_ingredient):
            return [RecipeIngredient(note=x) for x in recipe_ingredient]

        return recipe_ingredient
