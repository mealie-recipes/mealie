from mealie.services.scraper.scraper_strategies import safe_scrape_html

from ..base import WorkflowStep
from ..compilers import DEFAULT_SOURCE_COMPILERS, SourceCompiler
from ..context import WorkflowContext
from ..exceptions import NoRecipeDataError


class CompileSourceStep(WorkflowStep):
    """
    Compiles the workflow input into a Compiled Source Document: a faithful transcription of
    the source material that later steps read instead of the raw input.
    """

    name = "compile-source"

    def __init__(self, compilers: list[type[SourceCompiler]] | None = None) -> None:
        self.compilers = DEFAULT_SOURCE_COMPILERS if compilers is None else compilers

    async def _fetch_source_content(self, ctx: WorkflowContext) -> str | None:
        if ctx.input.content:
            return ctx.input.content

        if not ctx.input.url:
            return None

        await ctx.report_progress("recipe.create-progress.fetching-webpage")
        return await safe_scrape_html(ctx.input.url) or None

    async def run(self, ctx: WorkflowContext) -> None:
        ctx.source_content = await self._fetch_source_content(ctx)
        if not (ctx.source_content or ctx.input.images):
            raise NoRecipeDataError("Unable to read any content from the provided source")

        for CompilerClass in self.compilers:
            compiler = CompilerClass(ctx, ctx.source_content)
            if not compiler.can_compile():
                continue

            if compiler.progress_key:
                await ctx.report_progress(compiler.progress_key)

            compiled = await compiler.compile()
            if not compiled:
                continue

            if not (compiled.contains_recipe and compiled.content.strip()):
                raise NoRecipeDataError("No recipe was found in the provided source")

            ctx.compiled_source = compiled
            return

        raise NoRecipeDataError("Unable to read any content from the provided source")
