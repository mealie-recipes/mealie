from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from requests import Session
from sqlalchemy import Column, ForeignKey, Integer, String, Table, orm

from .._model_utils import auto_init

ingredients_to_units = Table(
    "ingredients_to_units",
    SqlAlchemyBase.metadata,
    Column("ingredient_units.id", Integer, ForeignKey("ingredient_units.id")),
    Column("recipes_ingredients_id", Integer, ForeignKey("recipes_ingredients.id")),
)

ingredients_to_foods = Table(
    "ingredients_to_foods",
    SqlAlchemyBase.metadata,
    Column("ingredient_foods.id", Integer, ForeignKey("ingredient_foods.id")),
    Column("recipes_ingredients_id", Integer, ForeignKey("recipes_ingredients.id")),
)


class IngredientUnitModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "ingredient_units"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    abbreviation = Column(String)
    ingredients = orm.relationship("RecipeIngredient", secondary=ingredients_to_units, back_populates="unit")

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class IngredientFoodModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "ingredient_foods"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    ingredients = orm.relationship("RecipeIngredient", secondary=ingredients_to_foods, back_populates="food")

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class RecipeIngredient(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipes_ingredients"
    id = Column(Integer, primary_key=True)
    position = Column(Integer)
    parent_id = Column(Integer, ForeignKey("recipes.id"))

    title = Column(String)  # Section Header - Shows if Present
    note = Column(String)  # Force Show Text - Overrides Concat

    # Scaling Items
    unit = orm.relationship(IngredientUnitModel, secondary=ingredients_to_units, uselist=False)
    food = orm.relationship(IngredientFoodModel, secondary=ingredients_to_foods, uselist=False)
    quantity = Column(Integer)

    # Extras

    def __init__(self, title: str, note: str, unit: dict, food: dict, quantity: int, session: Session, **_) -> None:
        self.title = title
        self.note = note
        self.quantity = quantity

        if unit:
            self.unit = IngredientUnitModel.get_ref(unit.get("id"))

        if food:
            self.food = IngredientFoodModel.get_ref(unit.get("id"))
