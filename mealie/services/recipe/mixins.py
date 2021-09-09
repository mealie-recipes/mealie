from mealie.schema.recipe import Recipe
from mealie.schema.user.user import PrivateUser


def recipe_creation_factory(user: PrivateUser, name: str, additional_attrs: dict = None) -> Recipe:
    """
    The main creation point for recipes. The factor method returns an instance of the
    Recipe Schema class with the appropriate defaults set. Recipes shoudld not be created
    else-where to avoid conflicts.
    """
    additional_attrs = additional_attrs or {}
    additional_attrs["name"] = name
    additional_attrs["user_id"] = user.id
    additional_attrs["group_id"] = user.group_id

    return Recipe(**additional_attrs)
