import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID


def api_extras(func):
    """Decorator function to unpack the extras into a dict; requires an "extras" column"""

    def wrapper(*args, **kwargs):
        extras = kwargs.pop("extras")

        if extras is None:
            extras = []
        else:
            extras = [{"key": key, "value": value} for key, value in extras.items()]

        return func(*args, extras=extras, **kwargs)

    return wrapper


class ExtrasGeneric:
    """
    Template for API extensions

    This class is not an actual table, so it does not inherit from SqlAlchemyBase
    """

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    key_name: Mapped[str | None] = mapped_column(sa.String)
    value: Mapped[str | None] = mapped_column(sa.String)

    def __init__(self, key, value) -> None:
        self.key_name = key
        self.value = value


# used specifically for recipe extras
class ApiExtras(ExtrasGeneric, SqlAlchemyBase):
    __tablename__ = "api_extras"
    recipee_id: Mapped[GUID | None] = mapped_column(GUID, sa.ForeignKey("recipes.id"), index=True)


class IngredientFoodExtras(ExtrasGeneric, SqlAlchemyBase):
    __tablename__ = "ingredient_food_extras"
    ingredient_food_id: Mapped[GUID | None] = mapped_column(GUID, sa.ForeignKey("ingredient_foods.id"), index=True)


class ShoppingListExtras(ExtrasGeneric, SqlAlchemyBase):
    __tablename__ = "shopping_list_extras"
    shopping_list_id: Mapped[GUID | None] = mapped_column(GUID, sa.ForeignKey("shopping_lists.id"), index=True)


class ShoppingListItemExtras(ExtrasGeneric, SqlAlchemyBase):
    __tablename__ = "shopping_list_item_extras"
    shopping_list_item_id: Mapped[GUID | None] = mapped_column(
        GUID, sa.ForeignKey("shopping_list_items.id"), index=True
    )
