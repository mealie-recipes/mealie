import sqlalchemy as sa

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

    id = sa.Column(sa.Integer, primary_key=True)
    key_name = sa.Column(sa.String)
    value = sa.Column(sa.String)

    def __init__(self, key, value) -> None:
        self.key_name = key
        self.value = value


# used specifically for recipe extras
class ApiExtras(ExtrasGeneric, SqlAlchemyBase):
    __tablename__ = "api_extras"
    recipee_id = sa.Column(GUID, sa.ForeignKey("recipes.id"))


class IngredientFoodExtras(ExtrasGeneric, SqlAlchemyBase):
    __tablename__ = "ingredient_food_extras"
    ingredient_food_id = sa.Column(GUID, sa.ForeignKey("ingredient_foods.id"))


class ShoppingListExtras(ExtrasGeneric, SqlAlchemyBase):
    __tablename__ = "shopping_list_extras"
    shopping_list_id = sa.Column(GUID, sa.ForeignKey("shopping_lists.id"))


class ShoppingListItemExtras(ExtrasGeneric, SqlAlchemyBase):
    __tablename__ = "shopping_list_item_extras"
    shopping_list_item_id = sa.Column(GUID, sa.ForeignKey("shopping_list_items.id"))
