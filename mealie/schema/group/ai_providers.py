from typing import Any, Self

from pydantic import UUID4, ConfigDict, Field, ValidationInfo, computed_field, field_validator, model_validator
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.group.ai_providers import AIProvider, AIProviderSettings
from mealie.schema._mealie import MealieModel


class AIProviderCreate(MealieModel):
    name: str
    base_url: str | None = None
    api_key: str = Field("", exclude=True)
    model: str
    timeout: int = 300

    request_headers: dict[str, str] = {}
    request_params: dict[str, str] = {}

    @field_validator("name", "api_key", "model")
    def validate_not_empty(val: str, info: ValidationInfo) -> str:
        if not val:
            raise ValueError(f"{info.field_name} cannot be empty")

        return val

    @field_validator("base_url", mode="before")
    def validate_as_none(val: Any | None) -> Any | None:
        return val or None

    @field_validator("timeout")
    def validate_non_negative_number(val: int, info: ValidationInfo) -> int:
        if val < 0:
            raise ValueError(f"{info.field_name} cannot be less than zero")

        return val


class AIProviderSave(AIProviderCreate):
    settings_id: UUID4


class AIProviderUpdate(AIProviderCreate): ...


class AIProviderOut(AIProviderCreate):
    id: UUID4

    model_config = ConfigDict(from_attributes=True)

    @field_validator("request_headers", "request_params", mode="before")
    def wrap_headers_and_params(cls, v):
        if isinstance(v, dict):
            return v

        return {x.key_name: x.value for x in v} if v else {}

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(AIProvider.request_headers),
            selectinload(AIProvider.request_params),
        ]


class AIProviderSummary(MealieModel):
    id: UUID4
    name: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return []


class AIProviderSettingsCreate(MealieModel):
    group_id: UUID4


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


class AIProviderSettingsOut(AIProviderSettingsUpdate):
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
