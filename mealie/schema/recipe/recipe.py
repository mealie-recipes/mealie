from __future__ import annotations

import datetime
from numbers import Number
from pathlib import Path
from typing import Annotated, Any, ClassVar
from uuid import uuid4

from pydantic import UUID4, BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic_core.core_schema import ValidationInfo
from slugify import slugify
from sqlalchemy import Select
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.core.config import get_app_dirs
from mealie.core.exceptions import SlugError
from mealie.db.models.users.users import User
from mealie.schema._mealie import MealieModel, SearchType
from mealie.schema._mealie.mealie_model import MealieOutModel, UpdatedAtField
from mealie.schema.response.pagination import PaginationBase

from ...db.models.recipe import (
    RecipeComment,
    RecipeIngredientModel,
    RecipeIngredientSubstitutionModel,
    RecipeInstruction,
    RecipeModel,
)
from .recipe_asset import RecipeAsset
from .recipe_comments import RecipeCommentOut
from .recipe_notes import RecipeNote
from .recipe_nutrition import Nutrition
from .recipe_organizers import CategoryDraft, CategoryOut, TagDraft, TagOut, ToolDraft, ToolOut
from .recipe_settings import RecipeSettings
from .recipe_step import RecipeStep

app_dirs = get_app_dirs()


def create_recipe_slug(name: str, max_length: int = 250) -> str:
    """Generate a slug from a recipe name, truncating to a reasonable length.

    Args:
        name: The recipe name to create a slug from
        max_length: Maximum length for the slug (default: 250)

    Returns:
        A truncated slug string

    Raises:
        ValueError: If the name cannot be converted to a valid slug
    """
    generated_slug = slugify(name)
    if not generated_slug:
        raise SlugError("Recipe name cannot be empty or contain only special characters")
    if len(generated_slug) > max_length:
        generated_slug = generated_slug[:max_length]
    return generated_slug


class RecipeUrlCreate(BaseModel):
    url: str
    categories: list[CategoryDraft] | None = None
    tags: list[TagDraft] | None = None


class RecipeUrlBulkCreate(BaseModel):
    imports: list[RecipeUrlCreate]


class RecipeCreate(MealieModel):
    name: str


MAX_DURATION_SECONDS = 2**31 - 1
"""Postgres INTEGER max; SQLite would accept more, which would break moving data to Postgres"""

DurationSeconds = Annotated[int, Field(ge=0, le=MAX_DURATION_SECONDS)]


def _drop_legacy_int_id(value: Any) -> Any:
    # Old Mealie exports used integer ids, which mean nothing on this instance.
    return None if isinstance(value, int) else value


class RecipeDraft(MealieModel):
    """
    A recipe that is not saved yet, or a client's edit of a saved one.

    Scrapers, importers and migrations build drafts, and the recipe write routes accept them as request
    bodies. Every field is optional: RecipeService sets the owner when it saves a new draft, and the
    repository keeps the stored id and owner when a draft updates a saved recipe. Read a saved recipe
    back as `Recipe`, which guarantees those fields.

    A draft can carry an id before it is saved, so that files such as a scraped image can be written to
    the recipe's directory first.
    """

    id: UUID4 | None = None
    user_id: UUID4 | None = None
    household_id: UUID4 | None = None
    group_id: UUID4 | None = None

    name: str | None = None
    slug: Annotated[str, Field(validate_default=True)] = ""
    image: Any | None = None
    recipe_servings: float = 0
    recipe_yield_quantity: float = 0
    recipe_yield: str | None = None

    total_time: str | None = None
    prep_time: str | None = None
    perform_time: str | None = None
    total_time_seconds: DurationSeconds | None = None
    prep_time_seconds: DurationSeconds | None = None
    perform_time_seconds: DurationSeconds | None = None

    description: str | None = ""
    recipe_category: Annotated[list[CategoryDraft], Field(validate_default=True)] = []
    tags: Annotated[list[TagDraft], Field(validate_default=True)] = []
    tools: list[ToolDraft] = []
    rating: float | None = None
    org_url: str | None = Field(None, alias="orgURL")

    date_added: datetime.date | None = None
    date_updated: datetime.datetime | None = None
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = UpdatedAtField(None)

    recipe_ingredient: Annotated[list[RecipeIngredient], Field(validate_default=True)] = []
    recipe_instructions: list[RecipeStep] = []
    nutrition: Nutrition | None = None
    settings: RecipeSettings | None = None
    assets: list[RecipeAsset] = []
    notes: list[RecipeNote] = []
    extras: dict = {}
    comments: list[RecipeCommentOut] = []

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def accept_legacy_cook_time(cls, data: Any) -> Any:
        """Reads `cookTime` from older clients and exports as `performTime`, which replaced it."""
        if not isinstance(data, dict):
            return data

        cook_time = data.get("cookTime") or data.get("cook_time")
        has_perform_time = any(
            data.get(key) for key in ("performTime", "perform_time", "performTimeSeconds", "perform_time_seconds")
        )
        if cook_time and not has_perform_time:
            data = {**data, "performTime": cook_time}
        return data

    @field_validator("id", "user_id", "household_id", "group_id", mode="before")
    def drop_legacy_int_ids(cls, value: Any):
        return _drop_legacy_int_id(value)

    @field_validator("recipe_servings", "recipe_yield_quantity", mode="before")
    def clean_numbers(val: Any):
        return val or 0

    @field_validator("recipe_yield", "total_time", "prep_time", "perform_time", mode="before")
    def clean_strings(val: Any):
        if val is None:
            return val
        if isinstance(val, Number):
            return str(val)

        return val

    @field_validator("slug", mode="before")
    def validate_slug(cls, slug: str, info: ValidationInfo):
        if slug or not info.data.get("name"):
            return slug or ""

        return create_recipe_slug(info.data["name"])

    @field_validator("recipe_instructions", "assets", "notes", "comments", mode="before")
    def null_list_as_empty(value: Any):
        return [] if value is None else value

    @field_validator("recipe_ingredient", mode="before")
    def validate_ingredients(recipe_ingredient):
        if recipe_ingredient is None:
            return []
        if not isinstance(recipe_ingredient, list):
            return recipe_ingredient

        if recipe_ingredient and all(isinstance(elem, str) for elem in recipe_ingredient):
            return [RecipeIngredient(note=x) for x in recipe_ingredient]

        return recipe_ingredient

    @field_validator("tags", mode="before")
    def validate_tags(cats: Any):
        if cats is None:
            return []
        if isinstance(cats, list) and cats and isinstance(cats[0], str):
            return [TagDraft(id=uuid4(), name=c, slug=slugify(c)) for c in cats]
        return cats

    @field_validator("recipe_category", mode="before")
    def validate_categories(cats: Any):
        if cats is None:
            return []
        if isinstance(cats, list) and cats and isinstance(cats[0], str):
            return [CategoryDraft(id=uuid4(), name=c, slug=slugify(c)) for c in cats]
        return cats

    @field_validator("tools", mode="before")
    def validate_tools(tools: Any):
        if tools is None:
            return []
        if isinstance(tools, list) and tools and isinstance(tools[0], str):
            return [ToolDraft(id=uuid4(), name=t, slug=slugify(t)) for t in tools]
        return tools

    @field_validator("extras", mode="before")
    def convert_extras_to_dict(cls, v):
        if isinstance(v, dict):
            return v

        return {x.key_name: x.value for x in v} if v else {}

    @field_validator("nutrition", mode="before")
    def validate_nutrition(cls, v):
        return v or None


class RecipeSummary(MealieOutModel):
    """
    A saved recipe without its ingredients, instructions and other details, as list views show it.

    Every recipe has an owner: list queries skip rows whose user (and so household) is gone.
    """

    _normalize_search: ClassVar[bool] = True
    # Stricter than _fuzzy_similarity_threshold: at 0.5 short words in ingredient lines match far too
    # much ("salt" scores ~0.57 against "salmon").
    _fuzzy_ingredient_similarity_threshold: ClassVar[float] = 0.6

    id: UUID4
    user_id: UUID4
    household_id: UUID4
    group_id: UUID4

    name: str
    slug: str
    image: str | None = None
    recipe_servings: float = 0
    recipe_yield_quantity: float = 0
    recipe_yield: str | None = None

    total_time: str | None = None
    prep_time: str | None = None
    perform_time: str | None = None
    total_time_seconds: DurationSeconds | None = None
    prep_time_seconds: DurationSeconds | None = None
    perform_time_seconds: DurationSeconds | None = None

    description: str | None = ""
    recipe_category: list[CategoryOut] = []
    tags: list[TagOut] = []
    tools: list[ToolOut] = []
    rating: float | None = None
    org_url: str | None = Field(None, alias="orgURL")

    date_added: datetime.date | None = None
    date_updated: datetime.datetime | None = None
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = UpdatedAtField(None)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("recipe_servings", "recipe_yield_quantity", mode="before")
    def clean_numbers(val: Any):
        return val or 0

    @property
    def recipe_yield_display(self) -> str:
        # Fall back to recipe_servings when no yield is set at all, otherwise
        # a servings-only recipe emits a bare "0.0" (or "0.0 None") into schema.org.
        quantity = self.recipe_yield_quantity or (self.recipe_servings if not self.recipe_yield else 0)
        number = f"{quantity:g}" if quantity else ""
        return f"{number} {self.recipe_yield or ''}".strip()

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        # selectinload, not joinedload: joining three collections multiplies the rows per recipe
        # (categories x tags x tools), which made list pages several times slower.
        return [
            selectinload(RecipeModel.recipe_category),
            selectinload(RecipeModel.tags),
            selectinload(RecipeModel.tools).options(*ToolOut.loader_options()),
            joinedload(RecipeModel.user).load_only(User.household_id),
        ]


class RecipePagination(PaginationBase):
    items: list[RecipeSummary]


class RecipeOut(RecipeSummary):
    """A saved recipe with all of its details."""

    recipe_ingredient: list[RecipeIngredient] = []
    recipe_instructions: list[RecipeStep] = []
    nutrition: Nutrition = Field(default_factory=Nutrition)

    # Mealie Specific
    settings: RecipeSettings = Field(default_factory=RecipeSettings)
    assets: list[RecipeAsset] = []
    notes: list[RecipeNote] = []
    extras: dict = {}

    comments: list[RecipeCommentOut] = []

    model_config = ConfigDict(from_attributes=True)

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
        return self.directory_from_id(self.id)

    @property
    def asset_dir(self) -> Path:
        return self.asset_dir_from_id(self.id)

    @property
    def image_dir(self) -> Path:
        return self.image_dir_from_id(self.id)

    @field_validator("extras", mode="before")
    def convert_extras_to_dict(cls, v):
        if isinstance(v, dict):
            return v

        return {x.key_name: x.value for x in v} if v else {}

    @field_validator("nutrition", mode="before")
    def default_nutrition(cls, v):
        return v if v is not None else Nutrition()

    @field_validator("settings", mode="before")
    def default_settings(cls, v):
        return v if v is not None else RecipeSettings()

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(RecipeModel.assets),
            selectinload(RecipeModel.comments).joinedload(RecipeComment.user),
            selectinload(RecipeModel.extras),
            joinedload(RecipeModel.recipe_category),
            selectinload(RecipeModel.tags),
            selectinload(RecipeModel.tools).options(*ToolOut.loader_options()),
            joinedload(RecipeModel.user).load_only(User.household_id),
            selectinload(RecipeModel.recipe_ingredient)
            .joinedload(RecipeIngredientModel.unit)
            .options(*IngredientUnitOut.loader_options()),
            selectinload(RecipeModel.recipe_ingredient)
            .joinedload(RecipeIngredientModel.food)
            .options(*IngredientFoodOut.loader_options()),
            selectinload(RecipeModel.recipe_ingredient)
            .selectinload(RecipeIngredientModel.substitutions)
            .joinedload(RecipeIngredientSubstitutionModel.substitute_food),
            selectinload(RecipeModel.recipe_instructions).joinedload(RecipeInstruction.ingredient_references),
            selectinload(RecipeModel.recipe_instructions).joinedload(RecipeInstruction.note_references),
            joinedload(RecipeModel.nutrition),
            joinedload(RecipeModel.settings),
            # for whatever reason, joinedload can mess up the order here, so use selectinload just this once
            selectinload(RecipeModel.notes),
        ]

    @classmethod
    def filter_search_query(
        cls, db_model, query: Select, session: Session, search_type: SearchType, search: str, search_list: list[str]
    ) -> Select:
        from mealie.search.adapter import apply_search

        return apply_search(session, query, search)


class RecipeLastMade(BaseModel):
    timestamp: datetime.datetime


from mealie.schema.recipe.recipe_ingredient import IngredientFoodOut, IngredientUnitOut, RecipeIngredient  # noqa: E402

RecipeDraft.model_rebuild()
RecipeSummary.model_rebuild()
RecipeOut.model_rebuild()
