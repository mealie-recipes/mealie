import re
from collections import defaultdict
from functools import cache

from mealie.core.root_logger import get_logger
from mealie.lang.locale_config import LOCALE_CONFIG
from mealie.schema.openai.recipe import (
    OpenAIRecipe,
    OpenAIRecipeIngredient,
    OpenAIRecipeInstruction,
    OpenAIRecipeNotes,
)
from mealie.schema.recipe.recipe import Recipe
from mealie.services.scraper import cleaner

from ..base import WorkflowStep
from ..context import WorkflowContext
from ..recipe_conversion import to_recipe

TRANSLATE_RECIPE_PROMPT = "recipes.translate-recipe"

logger = get_logger()

MATCH_LANGUAGE_TAG = re.compile(r"^([a-z]{2,3})(?:[-_][a-z0-9]+)*$")
""" Matches ISO 639 codes and BCP 47 tags `de`, `de-DE`, `de_DE` and captures the language """

MATCH_LOCALE_NAME = re.compile(r"^(?P<native>.+?)\s*\((?P<english>.+)\)$")
""" Splits a locale name `Deutsch (German)` into its native and English names """


@cache
def _language_names() -> dict[str, str]:
    """
    Maps the language names known from the locale config, e.g. `deutsch` or `german`, to their
    ISO 639 code.

    Single words are included too, so that `English` matches `American English`, but only where
    they point to one language.
    """

    candidates: defaultdict[str, set[str]] = defaultdict(set)
    for key, config in LOCALE_CONFIG.items():
        code = key.split("-")[0].lower()
        name = config.name.lower()
        match = MATCH_LOCALE_NAME.match(name)
        names = [match["native"], match["english"]] if match else [name]

        for value in names:
            candidates[value].add(code)
            for word in value.split():
                candidates[word].add(code)

    return {name: codes.pop() for name, codes in candidates.items() if len(codes) == 1}


def language_code(language: str | None) -> str | None:
    """
    Normalizes a language to its ISO 639 code, so that a locale like `de-DE` and a name like
    `German` compare equal. Returns None if the language isn't recognized.
    """

    value = (language or "").strip().lower()
    if not value:
        return None

    if match := MATCH_LANGUAGE_TAG.match(value):
        return match[1]

    return _language_names().get(value)


class TranslateRecipeStep(WorkflowStep):
    """
    Translates the draft recipe into the language the caller asked for.

    Translating is its own request rather than a clause bolted onto the build prompt, so that
    neither prompt has to hedge about the other and the recipe being translated is already
    structured: the provider is handed discrete fields to translate instead of being asked to
    extract and translate in one pass.

    The step is optional. A translation that fails leaves an untranslated recipe behind, which
    is worth more to the user than discarding an import that otherwise succeeded.
    """

    name = "translate-recipe"
    progress_key = "recipe.create-progress.translating-recipe"
    required = False

    def should_run(self, ctx: WorkflowContext) -> bool:
        language = ctx.options.translate_language
        if not (language and ctx.draft_recipe):
            return False

        # nothing to do when the source is already written in the target language. A source whose
        # language is unknown is still translated, since it may well be written in another one
        source_language = ctx.compiled_source.language if ctx.compiled_source else None
        target_code, source_code = language_code(language), language_code(source_language)
        if target_code and source_code:
            return target_code != source_code

        return language.strip().lower() != (source_language or "").strip().lower()

    @staticmethod
    def _to_openai_recipe(recipe: Recipe) -> OpenAIRecipe:
        """
        Puts the draft recipe back into the provider's own schema.

        Sending the recipe in the shape it has to come back in is what keeps the translation
        aligned field by field. Nutrition is left out: by this point it holds bare numbers with
        fixed units, so there is nothing in it to translate.
        """

        return OpenAIRecipe(
            name=recipe.name or "",
            description=recipe.description,
            recipe_yield=recipe.recipe_yield,
            total_time=recipe.total_time,
            prep_time=recipe.prep_time,
            perform_time=recipe.perform_time,
            ingredients=[
                OpenAIRecipeIngredient(title=ingredient.title, text=ingredient.display)
                for ingredient in recipe.recipe_ingredient
                if ingredient.display
            ],
            instructions=[
                OpenAIRecipeInstruction(title=step.title, text=step.text)
                for step in recipe.recipe_instructions or []
                if step.text
            ],
            notes=[OpenAIRecipeNotes(title=note.title, text=note.text) for note in recipe.notes or [] if note.text],
        )

    def _build_message(self, ctx: WorkflowContext, recipe: Recipe) -> str:
        translatable = self._to_openai_recipe(recipe)

        return "\n\n".join(
            [
                f"Translate the recipe below into {ctx.options.translate_language}.",
                translatable.model_dump_json(exclude_none=True),
            ]
        )

    async def run(self, ctx: WorkflowContext) -> None:
        recipe = ctx.draft_recipe
        if not recipe:
            return

        response = await ctx.ai.get_response(
            ctx.ai.get_prompt(TRANSLATE_RECIPE_PROMPT),
            self._build_message(ctx, recipe),
            response_schema=OpenAIRecipe,
        )

        if not (response and (response.ingredients or response.instructions)):
            # a translation that came back empty would lose the recipe, so keep the original
            logger.error("Translation returned no recipe, keeping the untranslated one")
            return

        translated = to_recipe(ctx, response)
        # nutrition and structured times never made the round trip, so they carry over untouched
        translated.nutrition = recipe.nutrition
        translated.total_time_seconds = recipe.total_time_seconds
        translated.prep_time_seconds = recipe.prep_time_seconds
        translated.perform_time_seconds = recipe.perform_time_seconds

        # cleaning again is what parses the translated times and yield back out of their new wording
        cleaned = cleaner.clean(translated, ctx.translator)

        # the yield's numbers were parsed out before translating, so only its wording was sent.
        # Cleaning the translated wording finds no number in it, so the parsed ones carry over too
        cleaned.recipe_servings = recipe.recipe_servings
        cleaned.recipe_yield_quantity = recipe.recipe_yield_quantity

        ctx.draft_recipe = cleaned
