from __future__ import annotations

import datetime
import enum
from uuid import UUID, uuid4

from pydantic import UUID4, Field, validator
from pydantic.utils import GetterDict

from mealie.db.models.recipe.ingredient import IngredientFoodModel
from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.types import NoneFloat
from mealie.schema.response.pagination import PaginationBase


class UnitFoodBase(MealieModel):
    name: str
    description: str = ""
    extras: dict | None = {}


class CreateIngredientFood(UnitFoodBase):
    label_id: UUID4 | None = None


class SaveIngredientFood(CreateIngredientFood):
    group_id: UUID4


class IngredientFood(CreateIngredientFood):
    id: UUID4
    label: MultiPurposeLabelSummary | None = None
    created_at: datetime.datetime | None
    update_at: datetime.datetime | None

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(cls, name_orm: IngredientFoodModel):
            return {
                **GetterDict(name_orm),
                "extras": {x.key_name: x.value for x in name_orm.extras},
            }


class IngredientFoodPagination(PaginationBase):
    items: list[IngredientFood]


class CreateIngredientUnit(UnitFoodBase):
    fraction: bool = True
    abbreviation: str = ""
    use_abbreviation: bool = False


class SaveIngredientUnit(CreateIngredientUnit):
    group_id: UUID4


class IngredientUnit(CreateIngredientUnit):
    id: UUID4
    created_at: datetime.datetime | None
    update_at: datetime.datetime | None

    class Config:
        orm_mode = True


class IngredientUnitPagination(PaginationBase):
    items: list[IngredientUnit]


class RecipeIngredient(MealieModel):
    title: str | None
    note: str | None
    unit: IngredientUnit | CreateIngredientUnit | None
    food: IngredientFood | CreateIngredientFood | None
    disable_amount: bool = True
    quantity: NoneFloat = 1
    original_text: str | None

    # Ref is used as a way to distinguish between an individual ingredient on the frontend
    # It is required for the reorder and section titles to function properly because of how
    # Vue handles reactivity. ref may serve another purpose in the future.
    reference_id: UUID = Field(default_factory=uuid4)

    class Config:
        orm_mode = True

    @validator("quantity", pre=True)
    @classmethod
    def validate_quantity(cls, value, values) -> NoneFloat:
        """
        Sometimes the frontend UI will provide an empty string as a "null" value because of the default
        bindings in Vue. This validator will ensure that the quantity is set to None if the value is an
        empty string.
        """
        if isinstance(value, float):
            return round(value, 3)
        if value is None or value == "":
            return None
        return value


class IngredientConfidence(MealieModel):
    average: NoneFloat = None
    comment: NoneFloat = None
    name: NoneFloat = None
    unit: NoneFloat = None
    quantity: NoneFloat = None
    food: NoneFloat = None

    @validator("quantity", pre=True)
    @classmethod
    def validate_quantity(cls, value, values) -> NoneFloat:
        if isinstance(value, float):
            return round(value, 3)
        if value is None or value == "":
            return None
        return value


class ParsedIngredient(MealieModel):
    input: str | None
    confidence: IngredientConfidence = IngredientConfidence()
    ingredient: RecipeIngredient


class RegisteredParser(str, enum.Enum):
    nlp = "nlp"
    brute = "brute"


class IngredientsRequest(MealieModel):
    parser: RegisteredParser = RegisteredParser.nlp
    ingredients: list[str]


class IngredientRequest(MealieModel):
    parser: RegisteredParser = RegisteredParser.nlp
    ingredient: str


class MergeFood(MealieModel):
    from_food: UUID4
    to_food: UUID4


class MergeUnit(MealieModel):
    from_unit: UUID4
    to_unit: UUID4


from mealie.schema.labels.multi_purpose_label import MultiPurposeLabelSummary  # noqa: E402

IngredientFood.update_forward_refs()
