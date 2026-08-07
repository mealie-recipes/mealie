from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

from mealie.lang.providers import Translator
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.household.household import HouseholdInDB
from mealie.schema.openai.compiled_source import OpenAICompiledSource
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.user.user import PrivateUser
from mealie.services.openai import OpenAIService


class WorkflowInput(BaseModel):
    """The source material a recipe is imported from. At least one field must be populated."""

    content: str | None = None
    """Raw HTML, a JSON string of a https://schema.org/Recipe object, or plain text"""

    images: list[Path] = Field(default_factory=list)
    """Local paths to uploaded images, in order. The first is used as the recipe's cover image."""

    url: str | None = None
    """Source URL. Fetched if no content is supplied, and recorded as the recipe's original URL."""

    @property
    def is_empty(self) -> bool:
        return not (self.content or self.images or self.url)


class WorkflowOptions(BaseModel):
    """How the source material should be processed."""

    translate_language: str | None = None

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
    user: PrivateUser
    household: HouseholdInDB
    translator: Translator
    ai: OpenAIService

    on_progress: Callable[[str], Awaitable[None]] | None = None

    source_content: str | None = None
    """Input content, or the HTML fetched from the input URL"""

    compiled_source: OpenAICompiledSource | None = None
    """Output of the compile step"""

    draft_recipe: Recipe | None = None
    """Recipe under construction. Not persisted; the caller is responsible for saving it."""

    async def report_progress(self, key: str) -> None:
        if self.on_progress:
            await self.on_progress(self.translator.t(key))


class WorkflowResult(BaseModel):
    recipe: Recipe
    outcomes: dict[str, StepOutcome] = Field(default_factory=dict)
