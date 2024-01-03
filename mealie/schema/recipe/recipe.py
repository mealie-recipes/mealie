from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, ClassVar
from uuid import uuid4

from pydantic import UUID4, BaseModel, Field, validator
from slugify import slugify
from sqlalchemy import Select, desc, func, or_, select, text
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.core.config import get_app_dirs
from mealie.schema._mealie import MealieModel, SearchType
from mealie.schema.response.pagination import PaginationBase

from ...db.models.recipe import (
    IngredientFoodModel,
    RecipeComment,
    RecipeIngredientModel,
    RecipeInstruction,
    RecipeModel,
)
from ..getter_dict import ExtrasGetterDict
from .recipe_asset import RecipeAsset
from .recipe_comments import RecipeCommentOut
from .recipe_notes import RecipeNote
from .recipe_nutrition import Nutrition
from .recipe_settings import RecipeSettings
from .recipe_step import RecipeStep

app_dirs = get_app_dirs()


class RecipeTag(MealieModel):
    id: UUID4 | None = None
    name: str
    slug: str

    _searchable_properties: ClassVar[list[str]] = ["name"]

    class Config:
        orm_mode = True


class RecipeTagPagination(PaginationBase):
    items: list[RecipeTag]


class RecipeCategory(RecipeTag):
    pass


class RecipeCategoryPagination(PaginationBase):
    items: list[RecipeCategory]


class RecipeTool(RecipeTag):
    id: UUID4
    on_hand: bool = False


class RecipeToolPagination(PaginationBase):
    items: list[RecipeTool]


class CreateRecipeBulk(BaseModel):
    url: str
    categories: list[RecipeCategory] | None = None
    tags: list[RecipeTag] | None = None


class CreateRecipeByUrlBulk(BaseModel):
    imports: list[CreateRecipeBulk]


class CreateRecipe(MealieModel):
    name: str


class RecipeSummary(MealieModel):
    id: UUID4 | None
    _normalize_search: ClassVar[bool] = True

    user_id: UUID4 = Field(default_factory=uuid4)
    group_id: UUID4 = Field(default_factory=uuid4)

    name: str | None
    slug: str = ""
    image: Any | None
    recipe_yield: str | None

    total_time: str | None = None
    prep_time: str | None = None
    cook_time: str | None = None
    perform_time: str | None = None

    description: str | None = ""
    recipe_category: list[RecipeCategory] | None = []
    tags: list[RecipeTag] | None = []
    tools: list[RecipeTool] = []
    rating: int | None
    org_url: str | None = Field(None, alias="orgURL")

    date_added: datetime.date | None
    date_updated: datetime.datetime | None

    created_at: datetime.datetime | None
    update_at: datetime.datetime | None
    last_made: datetime.datetime | None

    class Config:
        orm_mode = True


class RecipePagination(PaginationBase):
    items: list[RecipeSummary]


class Recipe(RecipeSummary):
    recipe_ingredient: list[RecipeIngredient] = []
    recipe_instructions: list[RecipeStep] | None = []
    nutrition: Nutrition | None

    # Mealie Specific
    settings: RecipeSettings | None = None
    assets: list[RecipeAsset] | None = []
    notes: list[RecipeNote] | None = []
    extras: dict | None = {}

    comments: list[RecipeCommentOut] | None = []

    @staticmethod
    def _get_dir(dir: Path) -> Path:
        """Gets a directory and creates it if it doesn't exist"""

        dir.mkdir(exist_ok=True, parents=True)
        return dir

    @classmethod
    def directory_from_id(cls, recipe_id: UUID4 | str) -> Path:
        return cls._get_dir(app_dirs.RECIPE_DATA_DIR.joinpath(str(recipe_id)))

    @classmethod
    def asset_dir_from_id(cls, recipe_id: UUID4 | str) -> Path:
        return cls._get_dir(cls.directory_from_id(recipe_id).joinpath("assets"))

    @classmethod
    def image_dir_from_id(cls, recipe_id: UUID4 | str) -> Path:
        return cls._get_dir(cls.directory_from_id(recipe_id).joinpath("images"))

    @classmethod
    def timeline_image_dir_from_id(cls, recipe_id: UUID4 | str, timeline_event_id: UUID4 | str) -> Path:
        return cls._get_dir(cls.image_dir_from_id(recipe_id).joinpath("timeline").joinpath(str(timeline_event_id)))

    @property
    def directory(self) -> Path:
        if not self.id:
            raise ValueError("Recipe has no ID")

        return self.directory_from_id(self.id)

    @property
    def asset_dir(self) -> Path:
        if not self.id:
            raise ValueError("Recipe has no ID")

        return self.asset_dir_from_id(self.id)

    @property
    def image_dir(self) -> Path:
        if not self.id:
            raise ValueError("Recipe has no ID")

        return self.image_dir_from_id(self.id)

    class Config:
        orm_mode = True
        getter_dict = ExtrasGetterDict

    @classmethod
    def from_orm(cls, obj):
        recipe = super().from_orm(obj)
        recipe.__post_init__()
        return recipe

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__post_init__()

    def __post_init__(self) -> None:
        # the ingredient disable_amount property is unreliable,
        # so we set it here and recalculate the display property
        disable_amount = self.settings.disable_amount if self.settings else True
        for ingredient in self.recipe_ingredient:
            ingredient.disable_amount = disable_amount
            ingredient.is_food = not ingredient.disable_amount
            ingredient.display = ingredient._format_display()

    @validator("slug", always=True, pre=True, allow_reuse=True)
    def validate_slug(slug: str, values):  # type: ignore
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

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(RecipeModel.assets),
            selectinload(RecipeModel.comments).joinedload(RecipeComment.user),
            selectinload(RecipeModel.extras),
            joinedload(RecipeModel.recipe_category),
            selectinload(RecipeModel.tags),
            selectinload(RecipeModel.tools),
            selectinload(RecipeModel.recipe_ingredient).joinedload(RecipeIngredientModel.unit),
            selectinload(RecipeModel.recipe_ingredient)
            .joinedload(RecipeIngredientModel.food)
            .joinedload(IngredientFoodModel.extras),
            selectinload(RecipeModel.recipe_ingredient)
            .joinedload(RecipeIngredientModel.food)
            .joinedload(IngredientFoodModel.label),
            selectinload(RecipeModel.recipe_instructions).joinedload(RecipeInstruction.ingredient_references),
            joinedload(RecipeModel.nutrition),
            joinedload(RecipeModel.settings),
            # for whatever reason, joinedload can mess up the order here, so use selectinload just this once
            selectinload(RecipeModel.notes),
        ]

    @classmethod
    def filter_search_query(
        cls, db_model, query: Select, session: Session, search_type: SearchType, search: str, search_list: list[str]
    ) -> Select:
        """
        1. token search looks for any individual exact hit in name, description, and ingredients
        2. fuzzy search looks for trigram hits in name, description, and ingredients
        3. Sort order is determined by closeness to the recipe name
        Should search also look at tags?
        """

        if search_type is SearchType.fuzzy:
            # I would prefer to just do this in the recipe_ingredient.any part of the main query,
            # but it turns out that at least sqlite wont use indexes for that correctly anymore and
            # takes a big hit, so prefiltering it is
            ingredient_ids = (
                session.execute(
                    select(RecipeIngredientModel.id).filter(
                        or_(
                            RecipeIngredientModel.note_normalized.op("%>")(search),
                            RecipeIngredientModel.original_text_normalized.op("%>")(search),
                        )
                    )
                )
                .scalars()
                .all()
            )

            session.execute(text(f"set pg_trgm.word_similarity_threshold = {cls._fuzzy_similarity_threshold};"))
            return query.filter(
                or_(
                    RecipeModel.name_normalized.op("%>")(search),
                    RecipeModel.description_normalized.op("%>")(search),
                    RecipeModel.recipe_ingredient.any(RecipeIngredientModel.id.in_(ingredient_ids)),
                )
            ).order_by(  # trigram ordering could be too slow on million record db, but is fine with thousands.
                func.least(
                    RecipeModel.name_normalized.op("<->>")(search),
                )
            )

        else:
            ingredient_ids = (
                session.execute(
                    select(RecipeIngredientModel.id).filter(
                        or_(
                            *[RecipeIngredientModel.note_normalized.like(f"%{ns}%") for ns in search_list],
                            *[RecipeIngredientModel.original_text_normalized.like(f"%{ns}%") for ns in search_list],
                        )
                    )
                )
                .scalars()
                .all()
            )

            return query.filter(
                or_(
                    *[RecipeModel.name_normalized.like(f"%{ns}%") for ns in search_list],
                    *[RecipeModel.description_normalized.like(f"%{ns}%") for ns in search_list],
                    RecipeModel.recipe_ingredient.any(RecipeIngredientModel.id.in_(ingredient_ids)),
                )
            ).order_by(desc(RecipeModel.name_normalized.like(f"%{search}%")))


class RecipeLastMade(BaseModel):
    timestamp: datetime.datetime


from mealie.schema.recipe.recipe_ingredient import RecipeIngredient  # noqa: E402

RecipeSummary.update_forward_refs()
Recipe.update_forward_refs()
