from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.schema.recipe.recipe_notes import RecipeNote
from mealie.schema.recipe.recipe_step import RecipeStep
from mealie.schema.user.user import PrivateUser

step_text = """Recipe steps as well as other fields in the recipe page support markdown syntax.

Add a link [My Link](https://beta.mealie.io)
Imbed an image [My Image Text](https://myimagelink.com)

Bullet Points
- First
- Second

Number Lists
1. Number 1
2. Number 2
"""

ingredient_note = "1 Cup Flour"

note_text = "You can also add notes to recipes for additional helpful tips."


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

    recipe_ingredients = [RecipeIngredient(note=ingredient_note)]
    recipe_instructions = [RecipeStep(text=step_text)]
    notes = [RecipeNote(title="Helpful Tip", text=note_text)]

    return Recipe(
        recipe_ingredient=recipe_ingredients, notes=notes, recipe_instructions=recipe_instructions, **additional_attrs
    )
