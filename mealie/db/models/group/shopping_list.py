from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, orm
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models.labels import MultiPurposeLabel
from mealie.db.models.recipe.api_extras import ShoppingListExtras, ShoppingListItemExtras, api_extras

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import GUID, auto_init
from ..recipe.ingredient import IngredientFoodModel, IngredientUnitModel

if TYPE_CHECKING:
    from group import Group

    from ..recipe import RecipeModel


class ShoppingListItemRecipeReference(BaseMixins, SqlAlchemyBase):
    __tablename__ = "shopping_list_item_recipe_reference"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    shopping_list_item_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("shopping_list_items.id"), primary_key=True)
    recipe_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("recipes.id"), index=True)
    recipe: Mapped[Optional["RecipeModel"]] = orm.relationship("RecipeModel", back_populates="shopping_list_item_refs")
    recipe_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    recipe_scale: Mapped[float | None] = mapped_column(Float, default=1)
    recipe_note: Mapped[str | None] = mapped_column(String)

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class ShoppingListItem(SqlAlchemyBase, BaseMixins):
    __tablename__ = "shopping_list_items"

    # Id's
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    shopping_list_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("shopping_lists.id"), index=True)

    # Meta
    is_ingredient: Mapped[bool | None] = mapped_column(Boolean, default=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    checked: Mapped[bool | None] = mapped_column(Boolean, default=False)

    quantity: Mapped[float | None] = mapped_column(Float, default=1)
    note: Mapped[str | None] = mapped_column(String)

    is_food: Mapped[bool | None] = mapped_column(Boolean, default=False)
    extras: Mapped[list[ShoppingListItemExtras]] = orm.relationship(
        "ShoppingListItemExtras", cascade="all, delete-orphan"
    )

    # Scaling Items
    unit_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("ingredient_units.id"))
    unit: Mapped[IngredientUnitModel | None] = orm.relationship(IngredientUnitModel, uselist=False)

    food_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("ingredient_foods.id"))
    food: Mapped[IngredientFoodModel | None] = orm.relationship(IngredientFoodModel, uselist=False)

    label_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("multi_purpose_labels.id"))
    label: Mapped[MultiPurposeLabel | None] = orm.relationship(
        MultiPurposeLabel, uselist=False, back_populates="shopping_list_items"
    )

    # Recipe Reference
    recipe_references: Mapped[list[ShoppingListItemRecipeReference]] = orm.relationship(
        ShoppingListItemRecipeReference, cascade="all, delete, delete-orphan"
    )

    class Config:
        exclude = {"id", "label", "food", "unit"}

    @api_extras
    @auto_init()
    def __init__(self, **_) -> None:
        pass


class ShoppingListRecipeReference(BaseMixins, SqlAlchemyBase):
    __tablename__ = "shopping_list_recipe_reference"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    shopping_list_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("shopping_lists.id"), primary_key=True)

    recipe_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("recipes.id"), index=True)
    recipe: Mapped[Optional["RecipeModel"]] = orm.relationship(
        "RecipeModel", uselist=False, back_populates="shopping_list_refs"
    )

    recipe_quantity: Mapped[float] = mapped_column(Float, nullable=False)

    class Config:
        exclude = {"id", "recipe"}

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class ShoppingListMultiPurposeLabel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "shopping_lists_multi_purpose_labels"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    shopping_list_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("shopping_lists.id"), primary_key=True)
    shopping_list: Mapped["ShoppingList"] = orm.relationship("ShoppingList", back_populates="label_settings")
    label_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("multi_purpose_labels.id"), primary_key=True)
    label: Mapped["MultiPurposeLabel"] = orm.relationship(
        "MultiPurposeLabel", back_populates="shopping_lists_label_settings"
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    class Config:
        exclude = {"label"}

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class ShoppingList(SqlAlchemyBase, BaseMixins):
    __tablename__ = "shopping_lists"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    group_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="shopping_lists")

    name: Mapped[str | None] = mapped_column(String)
    list_items: Mapped[ShoppingListItem] = orm.relationship(
        ShoppingListItem,
        cascade="all, delete, delete-orphan",
        order_by="ShoppingListItem.position",
        collection_class=ordering_list("position"),
    )

    recipe_references: Mapped[ShoppingListRecipeReference] = orm.relationship(
        ShoppingListRecipeReference, cascade="all, delete, delete-orphan"
    )
    label_settings: Mapped[list["ShoppingListMultiPurposeLabel"]] = orm.relationship(
        ShoppingListMultiPurposeLabel,
        cascade="all, delete, delete-orphan",
        order_by="ShoppingListMultiPurposeLabel.position",
        collection_class=ordering_list("position"),
    )
    extras: Mapped[list[ShoppingListExtras]] = orm.relationship("ShoppingListExtras", cascade="all, delete-orphan")

    class Config:
        exclude = {"id", "list_items"}

    @api_extras
    @auto_init()
    def __init__(self, **_) -> None:
        pass
