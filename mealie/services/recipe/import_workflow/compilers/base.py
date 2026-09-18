from abc import ABC, abstractmethod
from enum import StrEnum

from mealie.core.root_logger import get_logger
from mealie.schema.openai.compiled_source import OpenAICompiledSource

from ..context import WorkflowContext

COMPILE_SOURCE_PROMPT = "recipes.compile-source"


class SourceType(StrEnum):
    """Which part of the workflow input a compiler reads."""

    IMAGES = "images"
    """Uploaded images"""

    URL = "url"
    """The URL itself, read without fetching it as a webpage, e.g. by downloading a video"""

    CONTENT = "content"
    """A block of text: the fetched page, or content the caller supplied"""


class SourceCompiler(ABC):
    """
    Turns one type of source material into a Compiled Source Document.

    Every source the input carries is compiled and the step merges the results, so a compiler
    only ever sees its own source and never has to account for the others. Within a source type
    compilers are tried in order and the first one that can handle the input wins, so a new input
    modality is a new compiler rather than another branch. Note that not every compiler calls an
    AI provider: sources that already contain structured data are compiled directly.
    """

    source_type: SourceType
    """Which part of the input this compiler reads"""

    progress_key: str | None = None
    """Translation key reported to the client before compiling. Left unset if compiling is instant."""

    def __init__(self, ctx: WorkflowContext, content: str | None = None) -> None:
        self.ctx = ctx
        # the text being compiled; only supplied to SourceType.CONTENT compilers
        self.content = content
        self.logger = get_logger()

    @abstractmethod
    def can_compile(self) -> bool: ...

    @abstractmethod
    async def compile(self) -> OpenAICompiledSource | None: ...
