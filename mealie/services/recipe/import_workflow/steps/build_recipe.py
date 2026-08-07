from pydantic.alias_generators import to_camel

from mealie.schema.openai.recipe import OpenAIRecipe
from mealie.schema.recipe.recipe import Recipe, create_recipe_slug
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.schema.recipe.recipe_notes import RecipeNote
from mealie.schema.recipe.recipe_nutrition import Nutrition
from mealie.schema.recipe.recipe_step import RecipeStep
from mealie.services.scraper import cleaner

from ..base import WorkflowStep
from ..context import WorkflowContext
from ..exceptions import NoRecipeDataError

BUILD_RECIPE_PROMPT = "recipes.build-recipe"


class BuildRecipeStep(WorkflowStep):
    """Turns the Compiled Source Document into a draft recipe."""

    name = "build-recipe"
    progress_key = "recipe.create-progress.creating-recipe-with-ai"

    def _build_message(self, ctx: WorkflowContext) -> str:
        compiled = ctx.compiled_source
        if not compiled:
            raise NoRecipeDataError("No source has been compiled")

        message_parts = ["Below is the transcribed recipe source.", compiled.content]

        translate_language = ctx.options.translate_language
        if translate_language and translate_language.lower() != (compiled.language or "").lower():
            message_parts.insert(
                0,
                f"Translate the recipe into {translate_language}. "
                "Translate every field, including ingredients and instructions.",
            )

        return "\n\n".join(message_parts)

    def _convert_nutrition(self, openai_recipe: OpenAIRecipe) -> Nutrition | None:
        if not openai_recipe.nutrition:
            return None

        # clean_nutrition expects schema.org's camelCase keys
        raw = {to_camel(key): value for key, value in openai_recipe.nutrition.model_dump().items()}
        cleaned = cleaner.clean_nutrition(raw)
        return Nutrition(**cleaned) if cleaned else None

    def _convert_recipe(self, ctx: WorkflowContext, openai_recipe: OpenAIRecipe) -> Recipe:
        compiled = ctx.compiled_source
        return Recipe(
            user_id=ctx.user.id,
            group_id=ctx.user.group_id,
            household_id=ctx.household.id,
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
            nutrition=self._convert_nutrition(openai_recipe),
            # uploaded images take precedence, and are attached to the recipe after it's created
            image=None if ctx.input.images else compiled and compiled.image_url,
            org_url=ctx.input.url,
        )

    def _clean_recipe(self, ctx: WorkflowContext, recipe: Recipe) -> Recipe:
        cleaned = cleaner.clean(recipe, ctx.translator)

        # cleaner.clean flattens ingredients and instructions into plain text, which drops their
        # section titles, so put ours back
        cleaned.recipe_ingredient = [
            RecipeIngredient(title=ingredient.title, note=cleaner.clean_string(ingredient.note or ""))
            for ingredient in recipe.recipe_ingredient
        ]
        cleaned.recipe_instructions = [
            RecipeStep(title=instruction.title, text=cleaner.clean_string(instruction.text))
            for instruction in recipe.recipe_instructions or []
        ]

        return cleaned

    async def run(self, ctx: WorkflowContext) -> None:
        response = await ctx.ai.get_response(
            ctx.ai.get_prompt(BUILD_RECIPE_PROMPT),
            self._build_message(ctx),
            response_schema=OpenAIRecipe,
        )

        if not response:
            raise NoRecipeDataError("The AI provider returned an empty response")

        if not (response.ingredients or response.instructions):
            raise NoRecipeDataError("No recipe was found in the provided source")

        ctx.draft_recipe = self._clean_recipe(ctx, self._convert_recipe(ctx, response))
