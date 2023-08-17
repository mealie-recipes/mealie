from __future__ import annotations

import datetime
import enum
from fractions import Fraction
from uuid import UUID, uuid4

from pydantic import UUID4, Field, validator
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.recipe import IngredientFoodModel
from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.types import NoneFloat
from mealie.schema.getter_dict import ExtrasGetterDict
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
        getter_dict = ExtrasGetterDict

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [joinedload(IngredientFoodModel.extras), joinedload(IngredientFoodModel.label)]


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


class RecipeIngredientBase(MealieModel):
    quantity: NoneFloat = 1
    unit: IngredientUnit | CreateIngredientUnit | None
    food: IngredientFood | CreateIngredientFood | None
    note: str | None = ""

    is_food: bool | None = None
    disable_amount: bool | None = None
    display: str = ""
    """
    How the ingredient should be displayed

    Automatically calculated after the object is created, unless overwritten
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # calculate missing is_food and disable_amount values
        # we can't do this in a validator since they depend on each other
        if self.is_food is None and self.disable_amount is not None:
            self.is_food = not self.disable_amount
        elif self.disable_amount is None and self.is_food is not None:
            self.disable_amount = not self.is_food
        elif self.is_food is None and self.disable_amount is None:
            self.is_food = bool(self.food)
            self.disable_amount = not self.is_food

        # format the display property
        if not self.display:
            self.display = self._format_display()

    @validator("unit", pre=True)
    def validate_unit(cls, v):
        if isinstance(v, str):
            return CreateIngredientUnit(name=v)
        else:
            return v

    @validator("food", pre=True)
    def validate_food(cls, v):
        if isinstance(v, str):
            return CreateIngredientFood(name=v)
        else:
            return v

    def _format_quantity_for_display(self) -> str:
        """How the quantity should be displayed"""

        qty: float | Fraction

        # decimal
        if not self.unit or not self.unit.fraction:
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
                components.append(self.unit.abbreviation if self.unit.use_abbreviation else self.unit.name)

            if self.food:
                components.append(self.food.name)

            if self.note:
                components.append(self.note)

        return " ".join(components)


class IngredientUnitPagination(PaginationBase):
    items: list[IngredientUnit]


class RecipeIngredient(RecipeIngredientBase):
    title: str | None
    original_text: str | None
    disable_amount: bool = True

    # Ref is used as a way to distinguish between an individual ingredient on the frontend
    # It is required for the reorder and section titles to function properly because of how
    # Vue handles reactivity. ref may serve another purpose in the future.
    reference_id: UUID = Field(default_factory=uuid4)

    class Config:
        orm_mode = True

    @validator("quantity", pre=True)
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

    @validator("quantity", pre=True)
    @classmethod
    def validate_quantity(cls, value, values) -> NoneFloat:
        if isinstance(value, float):
            return round(value, INGREDIENT_QTY_PRECISION)
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
