from __future__ import annotations

from datetime import datetime
from fractions import Fraction

from pydantic import UUID4, validator
from pydantic.utils import GetterDict

from mealie.db.models.group.shopping_list import ShoppingList, ShoppingListItem
from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.types import NoneFloat
from mealie.schema.recipe.recipe_ingredient import (
    INGREDIENT_QTY_PRECISION,
    MAX_INGREDIENT_DENOMINATOR,
    IngredientFood,
    IngredientUnit,
    RecipeIngredient,
)
from mealie.schema.response.pagination import PaginationBase

SUPERSCRIPT = dict(zip("1234567890", "¹²³⁴⁵⁶⁷⁸⁹⁰", strict=False))
SUBSCRIPT = dict(zip("1234567890", "₁₂₃₄₅₆₇₈₉₀", strict=False))


class ShoppingListItemRecipeRefCreate(MealieModel):
    recipe_id: UUID4
    recipe_quantity: float = 0
    """the quantity of this item in a single recipe (scale == 1)"""

    recipe_scale: NoneFloat = 1
    """the number of times this recipe has been added"""

    @validator("recipe_quantity", pre=True)
    def default_none_to_zero(cls, v):
        return 0 if v is None else v


class ShoppingListItemRecipeRefUpdate(ShoppingListItemRecipeRefCreate):
    id: UUID4
    shopping_list_item_id: UUID4


class ShoppingListItemRecipeRefOut(ShoppingListItemRecipeRefUpdate):
    class Config:
        orm_mode = True


class ShoppingListItemBase(MealieModel):
    shopping_list_id: UUID4
    checked: bool = False
    position: int = 0

    is_food: bool = False

    note: str | None = ""
    quantity: float = 1

    food_id: UUID4 | None = None
    label_id: UUID4 | None = None
    unit_id: UUID4 | None = None

    extras: dict | None = {}


class ShoppingListItemCreate(ShoppingListItemBase):
    recipe_references: list[ShoppingListItemRecipeRefCreate] = []


class ShoppingListItemUpdate(ShoppingListItemBase):
    recipe_references: list[ShoppingListItemRecipeRefCreate | ShoppingListItemRecipeRefUpdate] = []


class ShoppingListItemUpdateBulk(ShoppingListItemUpdate):
    """Only used for bulk update operations where the shopping list item id isn't already supplied"""

    id: UUID4


class ShoppingListItemOut(ShoppingListItemBase):
    id: UUID4
    display: str = ""
    """
    How the ingredient should be displayed

    Automatically calculated after the object is created
    """

    food: IngredientFood | None
    label: MultiPurposeLabelSummary | None
    unit: IngredientUnit | None

    recipe_references: list[ShoppingListItemRecipeRefOut] = []

    created_at: datetime | None
    update_at: datetime | None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # if we're missing a label, but the food has a label, use that as the label
        if (not self.label) and (self.food and self.food.label):
            self.label = self.food.label
            self.label_id = self.label.id

        # format the display property
        if not self.display:
            self.display = self._format_display()

    def _format_quantity_for_display(self) -> str:
        """How the quantity should be displayed"""

        qty: float | Fraction

        # decimal
        if not self.unit or not self.unit.fraction:
            qty = round(self.quantity, INGREDIENT_QTY_PRECISION)
            if qty.is_integer():
                return str(int(qty))

            else:
                return str(qty)

        # fraction
        qty = Fraction(self.quantity).limit_denominator(MAX_INGREDIENT_DENOMINATOR)
        if qty.denominator == 1:
            return str(qty.numerator)

        if qty.numerator <= qty.denominator:
            return f"{SUPERSCRIPT[str(qty.numerator)]}⁄{SUBSCRIPT[str(qty.denominator)]}"

        # convert an improper fraction into a mixed fraction (e.g. 11/4 --> 2 3/4)
        whole_number = 0
        while qty.numerator > qty.denominator:
            whole_number += 1
            qty -= 1

        return f"{whole_number} {SUPERSCRIPT[str(qty.numerator)]}⁄{SUBSCRIPT[str(qty.denominator)]}"

    def _format_display(self) -> str:
        components = []

        # ingredients with no food come across with a qty of 1, which looks weird
        # e.g. "1 2 tbsp of olive oil"
        if self.quantity and (self.is_food or self.quantity != 1):
            components.append(self._format_quantity_for_display())

        if not self.is_food:
            components.append(self.note or "")

        else:
            if self.quantity and self.unit:
                components.append(self.unit.abbreviation if self.unit.use_abbreviation else self.unit.name)

            if self.food:
                components.append(self.food.name)

            if self.note:
                components.append(self.note)

        return " ".join(components)

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(cls, name_orm: ShoppingListItem):
            return {
                **GetterDict(name_orm),
                "extras": {x.key_name: x.value for x in name_orm.extras},
            }


class ShoppingListItemsCollectionOut(MealieModel):
    """Container for bulk shopping list item changes"""

    created_items: list[ShoppingListItemOut] = []
    updated_items: list[ShoppingListItemOut] = []
    deleted_items: list[ShoppingListItemOut] = []


class ShoppingListItemPagination(PaginationBase):
    items: list[ShoppingListItemOut]


class ShoppingListCreate(MealieModel):
    name: str | None = None
    extras: dict | None = {}

    created_at: datetime | None
    update_at: datetime | None


class ShoppingListRecipeRefOut(MealieModel):
    id: UUID4
    shopping_list_id: UUID4
    recipe_id: UUID4
    recipe_quantity: float
    """the number of times this recipe has been added"""

    recipe: RecipeSummary

    class Config:
        orm_mode = True


class ShoppingListSave(ShoppingListCreate):
    group_id: UUID4


class ShoppingListSummary(ShoppingListSave):
    id: UUID4

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(cls, name_orm: ShoppingList):
            return {
                **GetterDict(name_orm),
                "extras": {x.key_name: x.value for x in name_orm.extras},
            }


class ShoppingListPagination(PaginationBase):
    items: list[ShoppingListSummary]


class ShoppingListUpdate(ShoppingListSummary):
    list_items: list[ShoppingListItemOut] = []


class ShoppingListOut(ShoppingListUpdate):
    recipe_references: list[ShoppingListRecipeRefOut]

    class Config:
        orm_mode = True


class ShoppingListAddRecipeParams(MealieModel):
    recipe_increment_quantity: float = 1
    recipe_ingredients: list[RecipeIngredient] | None = None
    """optionally override which ingredients are added from the recipe"""


class ShoppingListRemoveRecipeParams(MealieModel):
    recipe_decrement_quantity: float = 1


from mealie.schema.labels.multi_purpose_label import MultiPurposeLabelSummary  # noqa: E402
from mealie.schema.recipe.recipe import RecipeSummary  # noqa: E402

ShoppingListRecipeRefOut.update_forward_refs()
ShoppingListItemOut.update_forward_refs()
