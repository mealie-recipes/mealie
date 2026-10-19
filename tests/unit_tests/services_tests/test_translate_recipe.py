import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from mealie.lang import get_locale_provider
from mealie.schema.openai.compiled_source import OpenAICompiledSource
from mealie.schema.openai.recipe import OpenAIRecipe, OpenAIRecipeIngredient, OpenAIRecipeInstruction
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.schema.recipe.recipe_step import RecipeStep
from mealie.services.recipe.import_workflow.compilers.structured_data import StructuredDataCompiler
from mealie.services.recipe.import_workflow.context import WorkflowContext, WorkflowInput, WorkflowOptions
from mealie.services.recipe.import_workflow.steps.translate_recipe import TranslateRecipeStep, language_code
from mealie.services.scraper import cleaner

translator = get_locale_provider("en-US")


def _ctx(
    translate_language: str | None = "en-US",
    source_language: str | None = None,
    response: OpenAIRecipe | None = None,
    content: str | None = None,
) -> WorkflowContext:
    ai = MagicMock()
    ai.get_prompt.return_value = "translate the recipe"
    ai.get_response = AsyncMock(return_value=response)

    return WorkflowContext(
        input=WorkflowInput(url="https://example.test/tzatziki", content=content),
        options=WorkflowOptions(translate_language=translate_language),
        repos=MagicMock(),
        translator=translator,
        ai=ai,
        compiled_source=OpenAICompiledSource(contains_recipe=True, content="Tzatziki", language=source_language),
    )


def _draft(recipe_yield: str) -> Recipe:
    """A draft recipe as the build step leaves it: already cleaned once."""

    recipe = Recipe(
        name="Veganes Tzatziki",
        recipe_yield=recipe_yield,
        total_time="PT10M",
        recipe_ingredient=[RecipeIngredient(note="500 g Sojajoghurt")],
        recipe_instructions=[RecipeStep(text="Alles verrühren.")],
    )
    return cleaner.clean(recipe, translator)


def _translation(recipe_yield: str | None) -> OpenAIRecipe:
    return OpenAIRecipe(
        name="Vegan Tzatziki",
        recipe_yield=recipe_yield,
        ingredients=[OpenAIRecipeIngredient(text="500 g soy yogurt")],
        instructions=[OpenAIRecipeInstruction(text="Stir everything together.")],
    )


@pytest.mark.asyncio
async def test_translating_keeps_the_servings():
    ctx = _ctx(response=_translation(None))
    ctx.draft_recipe = _draft("4 servings")
    assert ctx.draft_recipe.recipe_servings == 4

    await TranslateRecipeStep().run(ctx)

    assert ctx.draft_recipe.name == "Vegan Tzatziki"
    assert ctx.draft_recipe.recipe_servings == 4
    assert ctx.draft_recipe.recipe_yield_quantity == 0


@pytest.mark.asyncio
async def test_translating_keeps_the_yield_quantity_and_translates_its_wording():
    ctx = _ctx(response=_translation("pieces"))
    ctx.draft_recipe = _draft("12 Stücke")
    assert (ctx.draft_recipe.recipe_yield_quantity, ctx.draft_recipe.recipe_yield) == (12, "Stücke")

    await TranslateRecipeStep().run(ctx)

    assert ctx.draft_recipe.recipe_yield_quantity == 12
    assert ctx.draft_recipe.recipe_yield == "pieces"
    assert ctx.draft_recipe.recipe_servings == 0


@pytest.mark.asyncio
async def test_translating_keeps_the_structured_times():
    ctx = _ctx(response=_translation(None))
    ctx.draft_recipe = _draft("4 servings")
    assert ctx.draft_recipe.total_time_seconds == 600

    await TranslateRecipeStep().run(ctx)

    assert ctx.draft_recipe.total_time_seconds == 600


@pytest.mark.parametrize(
    "language, expected",
    [
        ("de-DE", "de"),
        ("de_de", "de"),
        ("DE", "de"),
        ("German", "de"),
        ("Deutsch", "de"),
        (" german ", "de"),
        ("English", "en"),
        ("Brazilian Portuguese", "pt"),
        ("Chinese", "zh"),
        ("Klingon", None),
        ("", None),
        (None, None),
    ],
)
def test_language_code(language: str | None, expected: str | None):
    assert language_code(language) == expected


@pytest.mark.parametrize(
    "target, source",
    [
        ("de-DE", "German"),
        ("de-DE", "Deutsch"),
        ("de-DE", "de"),
        ("en-US", "English"),
        ("en-GB", "en-US"),
    ],
)
def test_translation_is_skipped_when_the_source_is_in_the_target_language(target: str, source: str):
    ctx = _ctx(translate_language=target, source_language=source)
    ctx.draft_recipe = _draft("4 servings")

    assert not TranslateRecipeStep().should_run(ctx)


@pytest.mark.parametrize(
    "target, source",
    [
        ("en-US", "German"),
        ("de-DE", "fr-FR"),
        # a source of unknown language may be written in any language, so it's still translated
        ("de-DE", None),
        ("de-DE", "Klingon"),
    ],
)
def test_translation_runs_when_the_source_is_in_another_language(target: str, source: str | None):
    ctx = _ctx(translate_language=target, source_language=source)
    ctx.draft_recipe = _draft("4 servings")

    assert TranslateRecipeStep().should_run(ctx)


def test_translation_is_skipped_without_a_target_language():
    ctx = _ctx(translate_language=None, source_language="German")
    ctx.draft_recipe = _draft("4 servings")

    assert not TranslateRecipeStep().should_run(ctx)


LD_JSON = json.dumps({"@type": "Recipe", "name": "Veganes Tzatziki", "recipeYield": ["4", "4 Portionen"]})


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "html_tag, expected",
    [
        ('<html lang="de">', "de"),
        ('<html lang=" de-DE ">', "de-DE"),
        ('<html lang="">', None),
        ("<html>", None),
    ],
)
async def test_structured_data_reports_the_page_language(html_tag: str, expected: str | None):
    html = f'{html_tag}<head><script type="application/ld+json">{LD_JSON}</script></head><body></body></html>'
    compiler = StructuredDataCompiler(_ctx(), html)
    assert compiler.can_compile()

    compiled = await compiler.compile()

    assert compiled is not None
    assert compiled.language == expected
