from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

from mealie.lang.providers import Translator
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.household.household import HouseholdInDB
from mealie.schema.openai.compiled_source import OpenAICompiledSource
from mealie.schema.openai.organizers import OpenAIOrganizers
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.user.user import PrivateUser
from mealie.services.openai import OpenAIService


class WorkflowInput(BaseModel):
    """The source material a recipe is imported from. At least one field must be populated."""

    content: str | None = None
    """
    Content supplied by the caller: raw HTML, a JSON string of a https://schema.org/Recipe object,
    or plain text. Compiled in addition to any other source, never instead of one.
    """

    images: list[Path] = Field(default_factory=list)
    """Local paths to uploaded images, in order. The first is used as the recipe's cover image."""

    url: str | None = None
    """Source URL. Fetched unless `page_content` is set, and recorded as the recipe's original URL."""

    page_content: str | None = None
    """
    The page's own content, for callers that have already fetched it. Unlike `content` this is
    not a separate source, so supplying it skips the fetch rather than adding to the material.
    """

    @property
    def is_empty(self) -> bool:
        return not (self.content or self.images or self.url or self.page_content)


class WorkflowOptions(BaseModel):
    """How the source material should be processed."""

    translate_language: str | None = None

    resolve_organizers: bool = True
    """Whether to ask the provider for the recipe's tags, categories, and tools"""

    attach_organizers: bool = True
    """
    Whether resolved organizers should be attached to the recipe. Callers that apply organizers
    themselves can switch this off and read the names off the context instead.
    """

    create_new_organizers: bool = False
    """Whether organizers that don't already exist in the group should be created"""


class StepOutcome(StrEnum):
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class WorkflowContext:
    """Carries workflow inputs and accumulating state between steps."""

    input: WorkflowInput
    options: WorkflowOptions

    repos: AllRepositories
    translator: Translator
    ai: OpenAIService

    user: PrivateUser | None = None
    household: HouseholdInDB | None = None
    """Recipe owner. Optional, since callers that persist the recipe themselves assign it."""

    on_progress: Callable[[str], Awaitable[None]] | None = None

    compiled_source: OpenAICompiledSource | None = None
    """Output of the compile step: every source in the input, compiled and merged into one document"""

    organizer_names: OpenAIOrganizers | None = None
    """Organizer names returned by the organizer step, before they're matched to the database"""

    draft_recipe: Recipe | None = None
    """Recipe under construction. Not persisted; the caller is responsible for saving it."""

    async def report_progress(self, key: str) -> None:
        if self.on_progress:
            await self.on_progress(self.translator.t(key))


class WorkflowResult(BaseModel):
    recipe: Recipe
    outcomes: dict[str, StepOutcome] = Field(default_factory=dict)
