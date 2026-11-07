from enum import StrEnum
from typing import Any, Self

from pydantic import (
    UUID4,
    ConfigDict,
    Field,
    ValidationInfo,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.group.ai_providers import AIProvider, AIProviderSettings
from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.mealie_model import MealieOutModel

REDACTED_VALUE = "********"
"""Stands in for header and param values in API responses. Clients send it back to mean "keep the stored value"."""


class AIProviderCreate(MealieModel):
    name: str
    base_url: str | None = None
    api_key: str = Field("", exclude=True)
    model: str
    timeout: int = 300

    request_headers: dict[str, str] = {}
    request_params: dict[str, str] = {}

    @field_validator("name", "api_key", "model")
    def validate_not_empty(cls, val: str, info: ValidationInfo) -> str:
        if not val:
            raise ValueError(f"{info.field_name} cannot be empty")

        return val

    @field_validator("base_url", mode="before")
    def validate_as_none(val: Any | None) -> Any | None:
        return val or None

    @field_validator("timeout")
    def validate_non_negative_number(cls, val: int, info: ValidationInfo) -> int:
        if val < 0:
            raise ValueError(f"{info.field_name} cannot be less than zero")

        return val


class AIProviderUpdate(AIProviderCreate): ...


class AIProviderOut(AIProviderCreate, MealieOutModel):
    id: UUID4

    model_config = ConfigDict(from_attributes=True)

    @field_validator("request_headers", "request_params", mode="before")
    def wrap_headers_and_params(cls, v):
        if isinstance(v, dict):
            return v

        return {x.key_name: x.value for x in v} if v else {}

    @field_serializer("request_headers", "request_params", when_used="json")
    def redact_values(self, v: dict[str, str]) -> dict[str, str]:
        # Headers and params routinely carry credentials (e.g. Authorization), so like api_key they are write-only.
        return dict.fromkeys(v, REDACTED_VALUE)

    def resolve_update(self, data: AIProviderCreate) -> dict[str, Any]:
        """
        Fill omitted or redacted secrets in an edit from the stored values.

        Only while the base URL is unchanged, so a secret never goes to a host it was not saved for.
        """
        destination_changed = data.base_url != self.base_url

        if destination_changed and not data.api_key:
            raise ValueError("A new API key is required when the base URL changes")

        resolved = data.model_dump()
        resolved["api_key"] = data.api_key or self.api_key

        for field in ("request_headers", "request_params"):
            stored: dict[str, str] = getattr(self, field)
            submitted: dict[str, str] = resolved[field]
            for key, value in submitted.items():
                if value != REDACTED_VALUE:
                    continue

                if destination_changed or key not in stored:
                    raise ValueError(f"A new value is required for {key} in {field}")

                submitted[key] = stored[key]

        return resolved

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(AIProvider.request_headers),
            selectinload(AIProvider.request_params),
        ]


class AIProviderTestResult(MealieModel):
    success: bool
    message: str | None = None
    # None when image support was never checked: the test failed, or an audio-only provider was tested by transcription.
    supports_images: bool | None = None


class AIProviderSummary(MealieOutModel):
    id: UUID4
    name: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return []


class AIPromptMode(StrEnum):
    append = "append"
    override = "override"


class AIPromptOverrideUpdate(MealieModel):
    mode: AIPromptMode
    content: str = Field(..., max_length=20000)

    @field_validator("content")
    def validate_not_blank(cls, val: str) -> str:
        if not val.strip():
            raise ValueError("content cannot be empty")

        return val


class AIPromptOverrideCreate(AIPromptOverrideUpdate):
    name: str
    base_prompt_hash: str | None = None


class AIPromptOverrideOut(AIPromptOverrideCreate, MealieOutModel):
    id: UUID4

    model_config = ConfigDict(from_attributes=True)


class AIPromptOut(MealieOutModel):
    name: str
    is_system: bool
    default_content: str

    # Unset when the prompt isn't customized
    mode: AIPromptMode | None = None
    content: str | None = None

    # Whether the built-in prompt has changed since it was overridden
    default_changed: bool = False


class AIPromptsOut(MealieOutModel):
    global_instructions: str | None = None
    prompts: list[AIPromptOut]


class AIProviderSettingsUpdate(MealieModel):
    default_provider_id: UUID4 | None
    audio_provider_id: UUID4 | None
    image_provider_id: UUID4 | None

    @field_validator("default_provider_id", "audio_provider_id", "image_provider_id", mode="before")
    def validate_as_none(val: Any | None) -> Any | None:
        return val or None

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            joinedload(AIProviderSettings.default_provider),
            joinedload(AIProviderSettings.audio_provider),
            joinedload(AIProviderSettings.image_provider),
        ]


class AIProviderSettingsOut(AIProviderSettingsUpdate, MealieOutModel):
    providers: list[AIProviderSummary]

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def validate_providers(self) -> Self:
        existing_ids = {provider.id for provider in self.providers}
        for provider_id_name in ["default_provider_id", "audio_provider_id", "image_provider_id"]:
            if not (val := getattr(self, provider_id_name, None)):
                continue

            if val not in existing_ids:
                setattr(self, provider_id_name, None)

        return self

    @computed_field  # type: ignore[misc]
    @property
    def ai_enabled(self) -> bool:
        return self.default_provider_id is not None

    @computed_field  # type: ignore[misc]
    @property
    def audio_provider_enabled(self) -> bool:
        return self.ai_enabled and self.audio_provider_id is not None

    @computed_field  # type: ignore[misc]
    @property
    def image_provider_enabled(self) -> bool:
        return self.ai_enabled and self.image_provider_id is not None

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(AIProviderSettings.providers),
            joinedload(AIProviderSettings.default_provider),
            joinedload(AIProviderSettings.audio_provider),
            joinedload(AIProviderSettings.image_provider),
        ]
