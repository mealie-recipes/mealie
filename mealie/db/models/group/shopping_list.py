from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, orm
from sqlalchemy.ext.orderinglist import ordering_list

from mealie.db.models.labels import MultiPurposeLabel

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import GUID, auto_init
from ..recipe.ingredient import IngredientFoodModel, IngredientUnitModel


class ShoppingListItemRecipeReference(BaseMixins, SqlAlchemyBase):
    __tablename__ = "shopping_list_item_recipe_reference"
    id = Column(GUID, primary_key=True, default=GUID.generate)

    shopping_list_item_id = Column(GUID, ForeignKey("shopping_list_items.id"), primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    recipe = orm.relationship("RecipeModel", back_populates="shopping_list_item_refs")
    recipe_quantity = Column(Float, nullable=False)

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class ShoppingListItem(SqlAlchemyBase, BaseMixins):
    __tablename__ = "shopping_list_items"

    # Id's
    id = Column(GUID, primary_key=True, default=GUID.generate)
    shopping_list_id = Column(GUID, ForeignKey("shopping_lists.id"))

    # Meta
    is_ingredient = Column(Boolean, default=True)
    position = Column(Integer, nullable=False, default=0)
    checked = Column(Boolean, default=False)

    quantity = Column(Float, default=1)
    note = Column(String)

    is_food = Column(Boolean, default=False)

    # Scaling Items
    unit_id = Column(Integer, ForeignKey("ingredient_units.id"))
    unit = orm.relationship(IngredientUnitModel, uselist=False)

    food_id = Column(Integer, ForeignKey("ingredient_foods.id"))
    food = orm.relationship(IngredientFoodModel, uselist=False)

    label_id = Column(GUID, ForeignKey("multi_purpose_labels.id"))
    label = orm.relationship(MultiPurposeLabel, uselist=False, back_populates="shopping_list_items")

    # Recipe Reference
    recipe_references = orm.relationship(ShoppingListItemRecipeReference, cascade="all, delete, delete-orphan")

    class Config:
        exclude = {"id", "label", "food", "unit"}

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class ShoppingListRecipeReference(BaseMixins, SqlAlchemyBase):
    __tablename__ = "shopping_list_recipe_reference"
    id = Column(GUID, primary_key=True, default=GUID.generate)

    shopping_list_id = Column(GUID, ForeignKey("shopping_lists.id"), primary_key=True)

    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    recipe = orm.relationship("RecipeModel", uselist=False, back_populates="shopping_list_refs")

    recipe_quantity = Column(Float, nullable=False)

    class Config:
        exclude = {"id", "recipe"}

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class ShoppingList(SqlAlchemyBase, BaseMixins):
    __tablename__ = "shopping_lists"
    id = Column(GUID, primary_key=True, default=GUID.generate)

    group_id = Column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group = orm.relationship("Group", back_populates="shopping_lists")

    name = Column(String)
    list_items = orm.relationship(
        ShoppingListItem,
        cascade="all, delete, delete-orphan",
        order_by="ShoppingListItem.position",
        collection_class=ordering_list("position"),
    )

    recipe_references = orm.relationship(ShoppingListRecipeReference, cascade="all, delete, delete-orphan")

    class Config:
        exclude = {"id", "list_items"}

    @auto_init()
    def __init__(self, **_) -> None:
        pass
