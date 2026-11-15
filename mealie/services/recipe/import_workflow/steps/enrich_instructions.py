from uuid import UUID

from mealie.schema.openai.recipe import OpenAIInstructionEnrichment, OpenAIInstructionEnrichments
from mealie.schema.recipe.recipe import RecipeDraft
from mealie.schema.recipe.recipe_step import IngredientReferences, NoteReference, RecipeStep
from mealie.services.scraper import cleaner

from ..base import WorkflowStep
from ..context import WorkflowContext

ENRICH_INSTRUCTIONS_PROMPT = "recipes.enrich-instructions"


def _single_line(text: str) -> str:
    return " ".join(text.split())


def _resolve_references(numbers: list[int], reference_ids: list[UUID]) -> list[UUID]:
    """Maps the provider's 1-based numbers to reference ids, dropping duplicates and numbers out of range."""

    resolved: list[UUID] = []
    for number in numbers:
        if 1 <= number <= len(reference_ids) and (reference_id := reference_ids[number - 1]) not in resolved:
            resolved.append(reference_id)

    return resolved


class EnrichInstructionsStep(WorkflowStep):
    """
    Adds details to the draft recipe's instruction steps: the ingredients and notes each step
    links to, the duration it states, and the heading it opens with.

    It's a request of its own, rather than part of the build prompt, so that smaller models only
    have one job per request. It runs after translation so the details are found in the recipe's
    final wording, and reads the draft rather than the source since every detail it adds refines
    data that's already in the recipe.
    """

    name = "enrich-instructions"
    progress_key = "recipe.create-progress.enriching-instructions"
    required = False

    def should_run(self, ctx: WorkflowContext) -> bool:
        return bool(ctx.draft_recipe and ctx.draft_recipe.recipe_instructions)

    @staticmethod
    def _build_message(recipe: RecipeDraft) -> str:
        ingredients: list[str] = []
        for number, ingredient in enumerate(recipe.recipe_ingredient, start=1):
            if ingredient.title:
                ingredients.append(f"[{_single_line(ingredient.title)}]")
            ingredients.append(f"{number}. {_single_line(ingredient.display)}")

        notes = [
            f"{number}. " + _single_line(f"{note.title}: {note.text}" if note.title else note.text)
            for number, note in enumerate(recipe.notes or [], start=1)
        ]
        steps = [
            f"{number}. {_single_line(step.text)}"
            for number, step in enumerate(recipe.recipe_instructions or [], start=1)
        ]

        sections = [("Ingredients", ingredients), ("Notes", notes), ("Instruction steps", steps)]
        return "\n\n".join(f"{heading}:\n" + "\n".join(lines) for heading, lines in sections if lines)

    @staticmethod
    def _apply(
        step: RecipeStep, details: OpenAIInstructionEnrichment, ingredient_ids: list[UUID], note_ids: list[UUID]
    ) -> None:
        if ingredient_refs := _resolve_references(details.ingredients, ingredient_ids):
            step.ingredient_references = [IngredientReferences(reference_id=ref) for ref in ingredient_refs]

        if note_refs := _resolve_references(details.notes, note_ids):
            step.note_references = [NoteReference(reference_id=ref) for ref in note_refs]

        if details.duration and (seconds := cleaner.clean_duration(details.duration)):
            step.duration_seconds = seconds

        summary, text = (details.summary or "").strip(), (details.text or "").strip()
        if summary and text and not step.summary:
            step.summary, step.text = summary, text

    async def run(self, ctx: WorkflowContext) -> None:
        recipe = ctx.draft_recipe
        if not (recipe and recipe.recipe_instructions):
            return

        response = await ctx.ai.get_response(
            ctx.ai.get_prompt(ENRICH_INSTRUCTIONS_PROMPT),
            self._build_message(recipe),
            response_schema=OpenAIInstructionEnrichments,
        )

        if not response:
            return

        steps = recipe.recipe_instructions
        ingredient_ids = [ingredient.reference_id for ingredient in recipe.recipe_ingredient]
        note_ids = [note.reference_id for note in recipe.notes or []]

        for details in response.instructions:
            if 1 <= details.step <= len(steps):
                self._apply(steps[details.step - 1], details, ingredient_ids, note_ids)
