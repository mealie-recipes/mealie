from mealie.services.scraper.fetch import safe_scrape_html

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

    async def _fetch_source_content(self, ctx: WorkflowContext) -> None:
        if ctx.source_content or not ctx.input.url:
            return

        await ctx.report_progress("recipe.create-progress.fetching-webpage")
        ctx.source_content = await safe_scrape_html(ctx.input.url) or None

    async def _compile(self, ctx: WorkflowContext, compilers: list[type[SourceCompiler]]) -> bool:
        for CompilerClass in compilers:
            compiler = CompilerClass(ctx)
            if not compiler.can_compile():
                continue

            if compiler.progress_key:
                await ctx.report_progress(compiler.progress_key)

            compiled = await compiler.compile()
            if not compiled:
                continue

            if not (compiled.contains_recipe and compiled.content.strip()):
                raise NoRecipeDataError(ctx.translator.t("recipe.import-errors.no-recipe-found"))

            ctx.compiled_source = compiled
            return True

        return False

    async def run(self, ctx: WorkflowContext) -> None:
        ctx.source_content = ctx.input.content

        # compilers that work from the input alone go first, so that a video URL is downloaded
        # rather than fetched and read as a webpage
        if await self._compile(ctx, [c for c in self.compilers if not c.requires_content]):
            return

        await self._fetch_source_content(ctx)
        if not ctx.source_content:
            raise NoRecipeDataError(ctx.translator.t("recipe.import-errors.unreadable-source"))

        if not await self._compile(ctx, [c for c in self.compilers if c.requires_content]):
            raise NoRecipeDataError(ctx.translator.t("recipe.import-errors.unreadable-source"))
