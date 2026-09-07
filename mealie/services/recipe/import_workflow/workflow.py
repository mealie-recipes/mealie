from mealie.core.root_logger import get_logger

from .base import WorkflowStep
from .context import StepOutcome, WorkflowContext, WorkflowResult
from .steps import BuildRecipeStep, CompileSourceStep, ResolveOrganizersStep, TranslateRecipeStep

DEFAULT_WORKFLOW_STEPS: list[WorkflowStep] = [
    CompileSourceStep(),
    BuildRecipeStep(),
    TranslateRecipeStep(),
    ResolveOrganizersStep(),
]


class RecipeImportWorkflow:
    """
    Turns arbitrary source material into a recipe by running a series of steps in order.

    Run by the `/recipes/create/ai` route and by `RecipeScraperOpenAI`, the fallback strategy for
    `/recipes/create/url`. The other scraper strategies don't use it, so an ordinary URL import of
    a well-marked-up site never runs the workflow at all.

    The workflow never persists the recipe; it returns a draft for the caller to save.
    """

    def __init__(self, steps: list[WorkflowStep] | None = None) -> None:
        self.steps = DEFAULT_WORKFLOW_STEPS if steps is None else steps
        self.logger = get_logger()

    async def run(self, ctx: WorkflowContext) -> WorkflowResult:
        outcomes: dict[str, StepOutcome] = {}

        for step in self.steps:
            if not step.should_run(ctx):
                self.logger.debug(f"Skipping workflow step {step.name}")
                outcomes[step.name] = StepOutcome.SKIPPED
                continue

            if step.progress_key:
                await ctx.report_progress(step.progress_key)

            try:
                await step.run(ctx)
                outcomes[step.name] = StepOutcome.COMPLETED
            except Exception:
                if step.required:
                    raise

                self.logger.exception(f"Optional workflow step {step.name} failed, continuing")
                outcomes[step.name] = StepOutcome.FAILED

        self.logger.debug(f"Workflow finished: {', '.join(f'{name}={outcome}' for name, outcome in outcomes.items())}")

        if not ctx.draft_recipe:
            raise ValueError("Workflow completed without producing a recipe")

        return WorkflowResult(recipe=ctx.draft_recipe, outcomes=outcomes)
