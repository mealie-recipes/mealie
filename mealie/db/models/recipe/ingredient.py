from mealie.db.models.model_base import BaseMixins, SqlAlchemyBase
from requests import Session
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, orm

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


class IngredientUnit(SqlAlchemyBase, BaseMixins):
    __tablename__ = "ingredient_units"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    ingredients = orm.relationship("RecipeIngredient", secondary=ingredients_to_units, back_populates="unit")

    def __init__(self, name: str, description: str = None) -> None:
        self.name = name
        self.description = description

    @classmethod
    def get_ref_or_create(cls, session: Session, obj: dict):
        # sourcery skip: flip-comparison
        if obj is None:
            return None

        name = obj.get("name")

        unit = session.query(cls).filter("name" == name).one_or_none()

        if not unit:
            return cls(**obj)


class IngredientFood(SqlAlchemyBase, BaseMixins):
    __tablename__ = "ingredient_foods"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    ingredients = orm.relationship("RecipeIngredient", secondary=ingredients_to_foods, back_populates="food")

    def __init__(self, name: str, description: str = None) -> None:
        self.name = name
        self.description = description

    @classmethod
    def get_ref_or_create(cls, session: Session, obj: dict):
        # sourcery skip: flip-comparison
        if obj is None:
            return None

        name = obj.get("name")

        unit = session.query(cls).filter("name" == name).one_or_none()

        if not unit:
            return cls(**obj)


class RecipeIngredient(SqlAlchemyBase):
    __tablename__ = "recipes_ingredients"
    id = Column(Integer, primary_key=True)
    position = Column(Integer)
    parent_id = Column(Integer, ForeignKey("recipes.id"))

    title = Column(String)  # Section Header - Shows if Present
    note = Column(String)  # Force Show Text - Overrides Concat

    # Scaling Items
    unit = orm.relationship(IngredientUnit, secondary=ingredients_to_units, uselist=False)
    food = orm.relationship(IngredientFood, secondary=ingredients_to_foods, uselist=False)
    quantity = Column(Integer)

    # Extras
    disable_amount = Column(Boolean, default=False)

    def __init__(
        self, title: str, note: str, unit: dict, food: dict, quantity: int, disable_amount: bool, session: Session, **_
    ) -> None:
        self.title = title
        self.note = note
        self.unit = IngredientUnit.get_ref_or_create(session, unit)
        self.food = IngredientFood.get_ref_or_create(session, food)
        self.quantity = quantity
        self.disable_amount = disable_amount
