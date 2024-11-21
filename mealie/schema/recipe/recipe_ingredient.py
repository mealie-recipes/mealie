from __future__ import annotations

import datetime
import enum
from fractions import Fraction
from typing import ClassVar
from uuid import UUID, uuid4

from pydantic import UUID4, ConfigDict, Field, field_validator, model_validator
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.recipe import IngredientFoodModel
from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.mealie_model import UpdatedAtField
from mealie.schema._mealie.types import NoneFloat
from mealie.schema.response.pagination import PaginationBase

INGREDIENT_QTY_PRECISION = 3
MAX_INGREDIENT_DENOMINATOR = 32

SUPERSCRIPT = dict(zip("1234567890", "¹²³⁴⁵⁶⁷⁸⁹⁰", strict=False))
SUBSCRIPT = dict(zip("1234567890", "₁₂₃₄₅₆₇₈₉₀", strict=False))


def display_fraction(fraction: Fraction):
    return (
        "".join([SUPERSCRIPT[c] for c in str(fraction.numerator)])
        + "/"
        + "".join([SUBSCRIPT[c] for c in str(fraction.denominator)])
    )


class UnitFoodBase(MealieModel):
    id: UUID4 | None = None
    name: str
    plural_name: str | None = None
    description: str = ""
    extras: dict | None = {}

    @field_validator("id", mode="before")
    def convert_empty_id_to_none(cls, v):
        # sometimes the frontend will give us an empty string instead of null, so we convert it to None,
        # otherwise Pydantic will try to convert it to a UUID and fail
        if not v:
            v = None

        return v

    @field_validator("extras", mode="before")
    def convert_extras_to_dict(cls, v):
        if isinstance(v, dict):
            return v

        return {x.key_name: x.value for x in v} if v else {}


class CreateIngredientFoodAlias(MealieModel):
    name: str


class IngredientFoodAlias(CreateIngredientFoodAlias):
    model_config = ConfigDict(from_attributes=True)


class CreateIngredientFood(UnitFoodBase):
    label_id: UUID4 | None = None
    aliases: list[CreateIngredientFoodAlias] = []
    households_with_ingredient_food: list[str] = []


class SaveIngredientFood(CreateIngredientFood):
    group_id: UUID4


class IngredientFood(CreateIngredientFood):
    id: UUID4
    label: MultiPurposeLabelSummary | None = None
    aliases: list[IngredientFoodAlias] = []

    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = UpdatedAtField(None)

    _searchable_properties: ClassVar[list[str]] = [
        "name_normalized",
        "plural_name_normalized",
    ]
    _normalize_search: ClassVar[bool] = True
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(IngredientFoodModel.households_with_ingredient_food),
            joinedload(IngredientFoodModel.extras),
            joinedload(IngredientFoodModel.label),
        ]

    @field_validator("households_with_ingredient_food", mode="before")
    def convert_households_to_slugs(cls, v):
        if not v:
            return []

        try:
            return [household.slug for household in v]
        except AttributeError:
            return v

    def is_on_hand(self, household_slug: str) -> bool:
        return household_slug in self.households_with_tool


class IngredientFoodPagination(PaginationBase):
    items: list[IngredientFood]


class CreateIngredientUnitAlias(MealieModel):
    name: str


class IngredientUnitAlias(CreateIngredientUnitAlias):
    model_config = ConfigDict(from_attributes=True)


class CreateIngredientUnit(UnitFoodBase):
    fraction: bool = True
    abbreviation: str = ""
    plural_abbreviation: str | None = ""
    use_abbreviation: bool = False
    aliases: list[CreateIngredientUnitAlias] = []


class SaveIngredientUnit(CreateIngredientUnit):
    group_id: UUID4


class IngredientUnit(CreateIngredientUnit):
    id: UUID4
    aliases: list[IngredientUnitAlias] = []

    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = UpdatedAtField(None)

    _searchable_properties: ClassVar[list[str]] = [
        "name_normalized",
        "plural_name_normalized",
        "abbreviation_normalized",
        "plural_abbreviation_normalized",
    ]
    _normalize_search: ClassVar[bool] = True
    model_config = ConfigDict(from_attributes=True)


class RecipeIngredientBase(MealieModel):
    quantity: NoneFloat = 1
    unit: IngredientUnit | CreateIngredientUnit | None = None
    food: IngredientFood | CreateIngredientFood | None = None
    note: str | None = ""

    is_food: bool | None = None
    disable_amount: bool | None = None
    display: str = ""
    """
    How the ingredient should be displayed

    Automatically calculated after the object is created, unless overwritten
    """

    @model_validator(mode="after")
    def calculate_missing_food_flags(self):
        # calculate missing is_food and disable_amount values
        # we can't do this in a validator since they depend on each other
        if self.is_food is None and self.disable_amount is not None:
            self.is_food = not self.disable_amount
        elif self.disable_amount is None and self.is_food is not None:
            self.disable_amount = not self.is_food
        elif self.is_food is None and self.disable_amount is None:
            self.is_food = bool(self.food)
            self.disable_amount = not self.is_food

        return self

    @model_validator(mode="after")
    def format_display(self):
        if not self.display:
            self.display = self._format_display()

        return self

    @field_validator("unit", mode="before")
    @classmethod
    def validate_unit(cls, v):
        if isinstance(v, str):
            return CreateIngredientUnit(name=v)
        else:
            return v

    @field_validator("food", mode="before")
    @classmethod
    def validate_food(cls, v):
        if isinstance(v, str):
            return CreateIngredientFood(name=v)
        else:
            return v

    def _format_quantity_for_display(self) -> str:
        """How the quantity should be displayed"""

        qty: float | Fraction

        # decimal
        if self.unit and not self.unit.fraction:
            qty = round(self.quantity or 0, INGREDIENT_QTY_PRECISION)
            if qty.is_integer():
                return str(int(qty))

            else:
                return str(qty)

        # fraction
        qty = Fraction(self.quantity or 0).limit_denominator(MAX_INGREDIENT_DENOMINATOR)
        if qty.denominator == 1:
            return str(qty.numerator)

        if qty.numerator <= qty.denominator:
            return display_fraction(qty)

        # convert an improper fraction into a mixed fraction (e.g. 11/4 --> 2 3/4)
        whole_number = 0
        while qty.numerator > qty.denominator:
            whole_number += 1
            qty -= 1

        return f"{whole_number} {display_fraction(qty)}"

    def _format_unit_for_display(self) -> str:
        if not self.unit:
            return ""

        use_plural = self.quantity and self.quantity > 1
        unit_val = ""
        if self.unit.use_abbreviation:
            if use_plural:
                unit_val = self.unit.plural_abbreviation or self.unit.abbreviation
            else:
                unit_val = self.unit.abbreviation

        if not unit_val:
            if use_plural:
                unit_val = self.unit.plural_name or self.unit.name
            else:
                unit_val = self.unit.name

        return unit_val

    def _format_food_for_display(self) -> str:
        if not self.food:
            return ""

        use_plural = (not self.quantity) or self.quantity > 1
        if use_plural:
            return self.food.plural_name or self.food.name
        else:
            return self.food.name

    def _format_display(self) -> str:
        components = []

        use_food = True
        if self.is_food is False:
            use_food = False
        elif self.disable_amount is True:
            use_food = False

        # ingredients with no food come across with a qty of 1, which looks weird
        # e.g. "1 2 tbsp of olive oil"
        if self.quantity and (use_food or self.quantity != 1):
            components.append(self._format_quantity_for_display())

        if not use_food:
            components.append(self.note or "")
        else:
            if self.quantity and self.unit:
                components.append(self._format_unit_for_display())

            if self.food:
                components.append(self._format_food_for_display())

            if self.note:
                components.append(self.note)

        return " ".join(components).strip()


class IngredientUnitPagination(PaginationBase):
    items: list[IngredientUnit]


class RecipeIngredient(RecipeIngredientBase):
    title: str | None = None
    original_text: str | None = None
    disable_amount: bool = True

    # Ref is used as a way to distinguish between an individual ingredient on the frontend
    # It is required for the reorder and section titles to function properly because of how
    # Vue handles reactivity. ref may serve another purpose in the future.
    reference_id: UUID = Field(default_factory=uuid4)
    model_config = ConfigDict(from_attributes=True)

    @field_validator("quantity", mode="before")
    @classmethod
    def validate_quantity(cls, value) -> NoneFloat:
        """
        Sometimes the frontend UI will provide an empty string as a "null" value because of the default
        bindings in Vue. This validator will ensure that the quantity is set to None if the value is an
        empty string.
        """
        if isinstance(value, float):
            return round(value, INGREDIENT_QTY_PRECISION)
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

    @field_validator("quantity", mode="before")
    @classmethod
    def validate_quantity(cls, value, values) -> NoneFloat:
        if isinstance(value, float):
            return round(value, INGREDIENT_QTY_PRECISION)
        if value is None or value == "":
            return None
        return value


class ParsedIngredient(MealieModel):
    input: str | None = None
    confidence: IngredientConfidence = IngredientConfidence()
    ingredient: RecipeIngredient


class RegisteredParser(str, enum.Enum):
    nlp = "nlp"
    brute = "brute"
    openai = "openai"


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

IngredientFood.model_rebuild()
