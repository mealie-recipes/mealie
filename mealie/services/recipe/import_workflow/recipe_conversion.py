from pydantic.alias_generators import to_camel

from mealie.schema.openai.recipe import OpenAIRecipe
from mealie.schema.recipe.recipe import Recipe, create_recipe_slug
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.schema.recipe.recipe_notes import RecipeNote
from mealie.schema.recipe.recipe_nutrition import Nutrition
from mealie.schema.recipe.recipe_step import RecipeStep
from mealie.services.scraper import cleaner

from .context import WorkflowContext


def convert_nutrition(openai_recipe: OpenAIRecipe) -> Nutrition | None:
    if not openai_recipe.nutrition:
        return None

    # clean_nutrition expects schema.org's camelCase keys
    raw = {to_camel(key): value for key, value in openai_recipe.nutrition.model_dump().items()}
    cleaned = cleaner.clean_nutrition(raw)
    return Nutrition(**cleaned) if cleaned else None


def to_recipe(ctx: WorkflowContext, openai_recipe: OpenAIRecipe) -> Recipe:
    """
    Turns a provider's recipe into a draft recipe.

    Shared by every step that produces one, so that a recipe the provider rewrites, such as a
    translation, is converted exactly the way the original was.
    """

    compiled = ctx.compiled_source

    # callers that persist the recipe themselves assign its owner, so only set it when known
    owner = (
        {"user_id": ctx.user.id, "group_id": ctx.user.group_id, "household_id": ctx.household.id}
        if ctx.user and ctx.household
        else {}
    )

    return Recipe(
        **owner,
        name=openai_recipe.name,
        slug=create_recipe_slug(openai_recipe.name),
        description=openai_recipe.description,
        recipe_yield=openai_recipe.recipe_yield,
        total_time=openai_recipe.total_time,
        prep_time=openai_recipe.prep_time,
        perform_time=openai_recipe.perform_time,
        recipe_ingredient=[
            RecipeIngredient(title=ingredient.title, note=ingredient.text)
            for ingredient in openai_recipe.ingredients
            if ingredient.text
        ],
        recipe_instructions=[
            RecipeStep(title=instruction.title, text=instruction.text)
            for instruction in openai_recipe.instructions
            if instruction.text
        ],
        notes=[RecipeNote(title=note.title or "", text=note.text) for note in openai_recipe.notes if note.text],
        nutrition=convert_nutrition(openai_recipe),
        # uploaded images take precedence, and are attached to the recipe after it's created
        image=None if ctx.input.images else compiled and compiled.image_url,
        org_url=ctx.input.url,
    )
