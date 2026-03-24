from datetime import datetime

from pydantic import UUID4, ConfigDict

from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import PaginationBase


class RecipeVersionSummary(MealieModel):
    """Lightweight version info for listing (no snapshot)."""

    id: UUID4
    recipe_id: UUID4
    user_id: UUID4 | None = None
    group_id: UUID4
    version_number: int
    name: str
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class RecipeVersionOut(RecipeVersionSummary):
    """Full version including the JSON snapshot."""

    snapshot: str


class RecipeVersionPagination(PaginationBase):
    items: list[RecipeVersionSummary]


# ─── Diff types ───────────────────────────────────────────


class FieldDiff(MealieModel):
    field_name: str
    label: str
    old_value: str | None = None
    new_value: str | None = None


class IngredientDiff(MealieModel):
    position: int
    old_text: str | None = None
    new_text: str | None = None


class InstructionDiff(MealieModel):
    position: int
    old_text: str | None = None
    new_text: str | None = None


class RecipeDiff(MealieModel):
    """Structured diff between two recipe versions."""

    version_id: UUID4 | None = None
    compare_to: str = "current"  # version_id or "current"
    fields_changed: list[FieldDiff] = []
    ingredients_added: list[str] = []
    ingredients_removed: list[str] = []
    ingredients_changed: list[IngredientDiff] = []
    instructions_added: list[str] = []
    instructions_removed: list[str] = []
    instructions_changed: list[InstructionDiff] = []
    categories_added: list[str] = []
    categories_removed: list[str] = []
    tags_added: list[str] = []
    tags_removed: list[str] = []
