from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.schema.recipe.recipe_step import RecipeStep
from mealie.schema.user.user import PrivateUser

step_text = """Recipe steps as well as other fields in the recipe page support markdown syntax.

**Add a link**

[My Link](https://beta.mealie.io)

**Imbed an image**

Use the `height="100"` or `width="100"` attributes to set the size of the image.

<img height="100" src="https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=960&q=80"></img>

"""

ingredient_note = "1 Cup Flour"


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

    print(additional_attrs)

    if not additional_attrs.get("recipe_ingredient"):
        additional_attrs["recipe_ingredient"] = [RecipeIngredient(note=ingredient_note)]

    if not additional_attrs.get("recipe_instructions"):
        additional_attrs["recipe_instructions"] = [RecipeStep(text=step_text)]

    return Recipe(**additional_attrs)
