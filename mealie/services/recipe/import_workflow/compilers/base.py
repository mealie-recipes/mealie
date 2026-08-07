from abc import ABC, abstractmethod

from mealie.core.root_logger import get_logger
from mealie.schema.openai.compiled_source import OpenAICompiledSource

from ..context import WorkflowContext

COMPILE_SOURCE_PROMPT = "recipes.compile-source"


class SourceCompiler(ABC):
    """
    Turns one kind of source material into a Compiled Source Document.

    Compilers are tried in order and the first one that can handle the input wins, so a new
    input modality is a new compiler rather than another branch. Note that not every compiler
    calls an AI provider: sources that already contain structured data are compiled directly.
    """

    progress_key: str | None = None
    """Translation key reported to the client before compiling. Left unset if compiling is instant."""

    requires_content: bool = True
    """
    Whether the compiler needs the source content. Compilers that work from the input alone are
    offered the input first, so that e.g. a video URL is downloaded rather than fetched as a webpage.
    """

    def __init__(self, ctx: WorkflowContext) -> None:
        self.ctx = ctx
        self.logger = get_logger()

    @property
    def content(self) -> str | None:
        return self.ctx.source_content

    @abstractmethod
    def can_compile(self) -> bool: ...

    @abstractmethod
    async def compile(self) -> OpenAICompiledSource | None: ...
