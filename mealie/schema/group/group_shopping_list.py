from __future__ import annotations

from datetime import datetime

from pydantic import UUID4, validator
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.group import (
    ShoppingList,
    ShoppingListItem,
    ShoppingListMultiPurposeLabel,
    ShoppingListRecipeReference,
)
from mealie.db.models.recipe import IngredientFoodModel, RecipeModel
from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.types import NoneFloat
from mealie.schema.getter_dict import ExtrasGetterDict
from mealie.schema.labels.multi_purpose_label import MultiPurposeLabelSummary
from mealie.schema.recipe.recipe import RecipeSummary
from mealie.schema.recipe.recipe_ingredient import (
    IngredientFood,
    IngredientUnit,
    RecipeIngredient,
    RecipeIngredientBase,
)
from mealie.schema.response.pagination import PaginationBase


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


class ShoppingListItemBase(RecipeIngredientBase):
    shopping_list_id: UUID4
    checked: bool = False
    position: int = 0

    quantity: float = 1

    food_id: UUID4 | None = None
    label_id: UUID4 | None = None
    unit_id: UUID4 | None = None

    is_food: bool = False
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

    class Config:
        orm_mode = True
        getter_dict = ExtrasGetterDict

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(ShoppingListItem.extras),
            selectinload(ShoppingListItem.food).joinedload(IngredientFoodModel.extras),
            selectinload(ShoppingListItem.food).joinedload(IngredientFoodModel.label),
            joinedload(ShoppingListItem.label),
            joinedload(ShoppingListItem.unit),
            selectinload(ShoppingListItem.recipe_references),
        ]


class ShoppingListItemsCollectionOut(MealieModel):
    """Container for bulk shopping list item changes"""

    created_items: list[ShoppingListItemOut] = []
    updated_items: list[ShoppingListItemOut] = []
    deleted_items: list[ShoppingListItemOut] = []


class ShoppingListMultiPurposeLabelCreate(MealieModel):
    shopping_list_id: UUID4
    label_id: UUID4
    position: int = 0


class ShoppingListMultiPurposeLabelUpdate(ShoppingListMultiPurposeLabelCreate):
    id: UUID4


class ShoppingListMultiPurposeLabelOut(ShoppingListMultiPurposeLabelUpdate):
    label: MultiPurposeLabelSummary

    class Config:
        orm_mode = True

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [joinedload(ShoppingListMultiPurposeLabel.label)]


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

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(ShoppingListRecipeReference.recipe).joinedload(RecipeModel.recipe_category),
            selectinload(ShoppingListRecipeReference.recipe).joinedload(RecipeModel.tags),
            selectinload(ShoppingListRecipeReference.recipe).joinedload(RecipeModel.tools),
        ]


class ShoppingListSave(ShoppingListCreate):
    group_id: UUID4


class ShoppingListSummary(ShoppingListSave):
    id: UUID4
    recipe_references: list[ShoppingListRecipeRefOut]
    label_settings: list[ShoppingListMultiPurposeLabelOut]

    class Config:
        orm_mode = True
        getter_dict = ExtrasGetterDict

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(ShoppingList.extras),
            selectinload(ShoppingList.recipe_references)
            .joinedload(ShoppingListRecipeReference.recipe)
            .joinedload(RecipeModel.recipe_category),
            selectinload(ShoppingList.recipe_references)
            .joinedload(ShoppingListRecipeReference.recipe)
            .joinedload(RecipeModel.tags),
            selectinload(ShoppingList.recipe_references)
            .joinedload(ShoppingListRecipeReference.recipe)
            .joinedload(RecipeModel.tools),
            selectinload(ShoppingList.label_settings).joinedload(ShoppingListMultiPurposeLabel.label),
        ]


class ShoppingListPagination(PaginationBase):
    items: list[ShoppingListSummary]


class ShoppingListUpdate(ShoppingListSave):
    id: UUID4
    list_items: list[ShoppingListItemOut] = []


class ShoppingListOut(ShoppingListUpdate):
    recipe_references: list[ShoppingListRecipeRefOut]
    label_settings: list[ShoppingListMultiPurposeLabelOut]

    class Config:
        orm_mode = True
        getter_dict = ExtrasGetterDict

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(ShoppingList.extras),
            selectinload(ShoppingList.list_items).joinedload(ShoppingListItem.extras),
            selectinload(ShoppingList.list_items)
            .joinedload(ShoppingListItem.food)
            .joinedload(IngredientFoodModel.extras),
            selectinload(ShoppingList.list_items)
            .joinedload(ShoppingListItem.food)
            .joinedload(IngredientFoodModel.label),
            selectinload(ShoppingList.list_items).joinedload(ShoppingListItem.label),
            selectinload(ShoppingList.list_items).joinedload(ShoppingListItem.unit),
            selectinload(ShoppingList.list_items).joinedload(ShoppingListItem.recipe_references),
            selectinload(ShoppingList.recipe_references)
            .joinedload(ShoppingListRecipeReference.recipe)
            .joinedload(RecipeModel.recipe_category),
            selectinload(ShoppingList.recipe_references)
            .joinedload(ShoppingListRecipeReference.recipe)
            .joinedload(RecipeModel.tags),
            selectinload(ShoppingList.recipe_references)
            .joinedload(ShoppingListRecipeReference.recipe)
            .joinedload(RecipeModel.tools),
            selectinload(ShoppingList.label_settings).joinedload(ShoppingListMultiPurposeLabel.label),
        ]


class ShoppingListAddRecipeParams(MealieModel):
    recipe_increment_quantity: float = 1
    recipe_ingredients: list[RecipeIngredient] | None = None
    """optionally override which ingredients are added from the recipe"""


class ShoppingListRemoveRecipeParams(MealieModel):
    recipe_decrement_quantity: float = 1
