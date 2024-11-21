from __future__ import annotations

import datetime
from numbers import Number
from pathlib import Path
from typing import Annotated, Any, ClassVar
from uuid import uuid4

from pydantic import UUID4, BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo
from slugify import slugify
from sqlalchemy import Select, desc, func, or_, select, text
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.core.config import get_app_dirs
from mealie.db.models.users.users import User
from mealie.schema._mealie import MealieModel, SearchType
from mealie.schema._mealie.mealie_model import UpdatedAtField
from mealie.schema.response.pagination import PaginationBase

from ...db.models.recipe import (
    IngredientFoodModel,
    RecipeComment,
    RecipeIngredientModel,
    RecipeInstruction,
    RecipeModel,
)
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
    model_config = ConfigDict(from_attributes=True)


class RecipeTagPagination(PaginationBase):
    items: list[RecipeTag]


class RecipeCategory(RecipeTag):
    pass


class RecipeCategoryPagination(PaginationBase):
    items: list[RecipeCategory]


class RecipeTool(RecipeTag):
    id: UUID4
    households_with_tool: list[str] = []

    @field_validator("households_with_tool", mode="before")
    def convert_households_to_slugs(cls, v):
        if not v:
            return []

        try:
            return [household.slug for household in v]
        except AttributeError:
            return v


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
    id: UUID4 | None = None
    _normalize_search: ClassVar[bool] = True

    user_id: UUID4 = Field(default_factory=uuid4, validate_default=True)
    household_id: UUID4 = Field(default_factory=uuid4, validate_default=True)
    group_id: UUID4 = Field(default_factory=uuid4, validate_default=True)

    name: str | None = None
    slug: Annotated[str, Field(validate_default=True)] = ""
    image: Any | None = None
    recipe_servings: float = 0
    recipe_yield_quantity: float = 0
    recipe_yield: str | None = None

    total_time: str | None = None
    prep_time: str | None = None
    cook_time: str | None = None
    perform_time: str | None = None

    description: str | None = ""
    recipe_category: Annotated[list[RecipeCategory] | None, Field(validate_default=True)] | None = []
    tags: Annotated[list[RecipeTag] | None, Field(validate_default=True)] = []
    tools: list[RecipeTool] = []
    rating: float | None = None
    org_url: str | None = Field(None, alias="orgURL")

    date_added: datetime.date | None = None
    date_updated: datetime.datetime | None = None

    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = UpdatedAtField(None)
    last_made: datetime.datetime | None = None
    model_config = ConfigDict(from_attributes=True)

    @field_validator("recipe_yield", "total_time", "prep_time", "cook_time", "perform_time", mode="before")
    def clean_strings(val: Any):
        if val is None:
            return val
        if isinstance(val, Number):
            return str(val)

        return val

    @property
    def recipe_yield_display(self) -> str:
        return f"{self.recipe_yield_quantity} {self.recipe_yield}".strip()

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            joinedload(RecipeModel.recipe_category),
            joinedload(RecipeModel.tags),
            joinedload(RecipeModel.tools),
            joinedload(RecipeModel.user).load_only(User.household_id),
        ]


class RecipePagination(PaginationBase):
    items: list[RecipeSummary]


class Recipe(RecipeSummary):
    recipe_ingredient: Annotated[list[RecipeIngredient], Field(validate_default=True)] = []
    recipe_instructions: list[RecipeStep] | None = []
    nutrition: Nutrition | None = None

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

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def calculate_missing_food_flags_and_format_display(self):
        disable_amount = self.settings.disable_amount if self.settings else True
        for ingredient in self.recipe_ingredient:
            ingredient.disable_amount = disable_amount
            ingredient.is_food = not ingredient.disable_amount

            # recalculate the display property, since it depends on the disable_amount flag
            ingredient.display = ingredient._format_display()

        return self

    @field_validator("slug", mode="before")
    def validate_slug(slug: str, info: ValidationInfo):
        if not info.data.get("name"):
            return slug

        return slugify(info.data["name"])

    @field_validator("recipe_ingredient", mode="before")
    def validate_ingredients(recipe_ingredient):
        if not recipe_ingredient or not isinstance(recipe_ingredient, list):
            return recipe_ingredient

        if all(isinstance(elem, str) for elem in recipe_ingredient):
            return [RecipeIngredient(note=x) for x in recipe_ingredient]

        return recipe_ingredient

    @field_validator("tags", mode="before")
    def validate_tags(cats: list[Any]):
        if isinstance(cats, list) and cats and isinstance(cats[0], str):
            return [RecipeTag(id=uuid4(), name=c, slug=slugify(c)) for c in cats]
        return cats

    @field_validator("recipe_category", mode="before")
    def validate_categories(cats: list[Any]):
        if isinstance(cats, list) and cats and isinstance(cats[0], str):
            return [RecipeCategory(id=uuid4(), name=c, slug=slugify(c)) for c in cats]
        return cats

    @field_validator("group_id", mode="before")
    def validate_group_id(group_id: Any):
        if isinstance(group_id, int):
            return uuid4()
        return group_id

    @field_validator("household_id", mode="before")
    def validate_household_id(household_id: Any):
        if isinstance(household_id, int):
            return uuid4()
        return household_id

    @field_validator("user_id", mode="before")
    def validate_user_id(user_id: Any):
        if isinstance(user_id, int):
            return uuid4()
        return user_id

    @field_validator("extras", mode="before")
    def convert_extras_to_dict(cls, v):
        if isinstance(v, dict):
            return v

        return {x.key_name: x.value for x in v} if v else {}

    @field_validator("nutrition", mode="before")
    def validate_nutrition(cls, v):
        return v or None

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

RecipeSummary.model_rebuild()
Recipe.model_rebuild()
