from unittest.mock import AsyncMock, MagicMock

import pytest

from mealie.lang import get_locale_provider
from mealie.schema.openai.recipe import OpenAIInstructionEnrichment, OpenAIInstructionEnrichments
from mealie.schema.recipe.recipe import RecipeDraft
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.schema.recipe.recipe_notes import RecipeNote
from mealie.schema.recipe.recipe_step import RecipeStep
from mealie.services.recipe.import_workflow import (
    RecipeImportWorkflow,
    StepOutcome,
    WorkflowContext,
    WorkflowInput,
    WorkflowOptions,
    WorkflowStep,
)
from mealie.services.recipe.import_workflow.steps.enrich_instructions import EnrichInstructionsStep

translator = get_locale_provider("en-US")


def _recipe(steps: list[RecipeStep] | None = None) -> RecipeDraft:
    return RecipeDraft(
        name="Pancakes",
        recipe_ingredient=[
            RecipeIngredient(title="Batter", note="1 cup flour"),
            RecipeIngredient(note="2 eggs"),
        ],
        notes=[RecipeNote(title="Tip", text="Rest the batter overnight.")],
        recipe_instructions=steps
        if steps is not None
        else [
            RecipeStep(text="Make the batter: whisk the flour and eggs."),
            RecipeStep(text="Cook for 3 minutes per side."),
        ],
    )


def _ctx(recipe: RecipeDraft, response: OpenAIInstructionEnrichments | None = None) -> WorkflowContext:
    ai = MagicMock()
    ai.get_prompt.return_value = "enrich the instructions"
    ai.get_response = AsyncMock(return_value=response)

    return WorkflowContext(
        input=WorkflowInput(content="Pancakes"),
        options=WorkflowOptions(),
        repos=MagicMock(),
        translator=translator,
        ai=ai,
        draft_recipe=recipe,
    )


def _respond(*details: OpenAIInstructionEnrichment) -> OpenAIInstructionEnrichments:
    return OpenAIInstructionEnrichments(instructions=list(details))


def test_the_message_numbers_ingredients_notes_and_steps():
    recipe = _recipe([RecipeStep(text="Whisk the flour\nand eggs.")])

    message = EnrichInstructionsStep._build_message(recipe)

    assert message == (
        "Ingredients:\n[Batter]\n1. 1 cup flour\n2. 2 eggs\n\n"
        "Notes:\n1. Tip: Rest the batter overnight.\n\n"
        "Instruction steps:\n1. Whisk the flour and eggs."
    )


def test_the_step_is_skipped_without_instructions():
    assert not EnrichInstructionsStep().should_run(_ctx(_recipe([])))
    assert EnrichInstructionsStep().should_run(_ctx(_recipe()))


@pytest.mark.asyncio
async def test_ingredients_and_notes_are_linked_by_number():
    recipe = _recipe()
    flour, eggs = recipe.recipe_ingredient
    ctx = _ctx(recipe, _respond(OpenAIInstructionEnrichment(step=1, ingredients=[1, 2], notes=[1])))

    await EnrichInstructionsStep().run(ctx)

    first, second = recipe.recipe_instructions or []
    assert [ref.reference_id for ref in first.ingredient_references] == [flour.reference_id, eggs.reference_id]
    assert [ref.reference_id for ref in first.note_references] == [(recipe.notes or [])[0].reference_id]
    assert second.ingredient_references == []
    assert second.note_references == []


@pytest.mark.asyncio
async def test_duplicate_and_unknown_numbers_are_dropped():
    recipe = _recipe()
    flour = recipe.recipe_ingredient[0]
    ctx = _ctx(
        recipe,
        _respond(
            OpenAIInstructionEnrichment(step=1, ingredients=[1, 1, 0, 3], notes=[2]),
            OpenAIInstructionEnrichment(step=3, ingredients=[2]),
            OpenAIInstructionEnrichment(step=0, ingredients=[2]),
        ),
    )

    await EnrichInstructionsStep().run(ctx)

    first, second = recipe.recipe_instructions or []
    assert [ref.reference_id for ref in first.ingredient_references] == [flour.reference_id]
    assert first.note_references == []
    assert second.ingredient_references == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "duration, expected",
    [
        ("PT3M", 180),
        ("PT1H30M", 5400),
        ("until golden", None),
        (None, None),
    ],
)
async def test_durations_are_parsed(duration: str | None, expected: int | None):
    recipe = _recipe()
    ctx = _ctx(recipe, _respond(OpenAIInstructionEnrichment(step=2, duration=duration)))

    await EnrichInstructionsStep().run(ctx)

    assert (recipe.recipe_instructions or [])[1].duration_seconds == expected


@pytest.mark.asyncio
async def test_a_heading_replaces_the_step_text():
    recipe = _recipe()
    ctx = _ctx(
        recipe,
        _respond(OpenAIInstructionEnrichment(step=1, summary="Make the batter", text="whisk the flour and eggs.")),
    )

    await EnrichInstructionsStep().run(ctx)

    step = (recipe.recipe_instructions or [])[0]
    assert step.summary == "Make the batter"
    assert step.text == "whisk the flour and eggs."


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "summary, text",
    [
        ("Make the batter", None),
        ("Make the batter", "  "),
        (None, "whisk the flour and eggs."),
    ],
)
async def test_a_heading_without_its_text_is_ignored(summary: str | None, text: str | None):
    recipe = _recipe()
    ctx = _ctx(recipe, _respond(OpenAIInstructionEnrichment(step=1, summary=summary, text=text)))

    await EnrichInstructionsStep().run(ctx)

    step = (recipe.recipe_instructions or [])[0]
    assert step.summary == ""
    assert step.text == "Make the batter: whisk the flour and eggs."


@pytest.mark.asyncio
async def test_an_existing_heading_is_kept():
    recipe = _recipe([RecipeStep(summary="Batter", text="Make the batter: whisk the flour and eggs.")])
    ctx = _ctx(
        recipe,
        _respond(OpenAIInstructionEnrichment(step=1, summary="Make the batter", text="whisk the flour and eggs.")),
    )

    await EnrichInstructionsStep().run(ctx)

    step = (recipe.recipe_instructions or [])[0]
    assert step.summary == "Batter"
    assert step.text == "Make the batter: whisk the flour and eggs."


@pytest.mark.asyncio
async def test_no_response_leaves_the_recipe_alone():
    recipe = _recipe()
    before = recipe.model_dump()

    await EnrichInstructionsStep().run(_ctx(recipe, None))

    assert recipe.model_dump() == before


class SetDraftStep(WorkflowStep):
    name = "set-draft"

    def __init__(self, recipe: RecipeDraft) -> None:
        self.recipe = recipe

    async def run(self, ctx: WorkflowContext) -> None:
        ctx.draft_recipe = self.recipe


@pytest.mark.asyncio
async def test_a_failure_does_not_fail_the_import():
    recipe = _recipe()
    ctx = _ctx(recipe)
    ctx.draft_recipe = None
    ctx.ai.get_response = AsyncMock(side_effect=RuntimeError("provider unavailable"))

    result = await RecipeImportWorkflow([SetDraftStep(recipe), EnrichInstructionsStep()]).run(ctx)

    assert result.recipe is recipe
    assert result.outcomes[EnrichInstructionsStep.name] == StepOutcome.FAILED
