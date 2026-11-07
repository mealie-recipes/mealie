import sqlalchemy as sa
from fastapi import HTTPException, status
from pydantic import UUID4

from mealie.db.models.group.ai_providers import AIPromptOverride, AIProvider, AIProviderSettings
from mealie.schema.group.ai_providers import (
    AIPromptOverrideCreate,
    AIPromptOverrideOut,
    AIProviderCreate,
    AIProviderOut,
)

from .repository_generic import GroupRepositoryGeneric


def _get_settings_id(repo: GroupRepositoryGeneric) -> UUID4:
    return repo.session.execute(
        sa.select(AIProviderSettings.id).where(AIProviderSettings.group_id == repo.group_id)
    ).scalar_one()


class GroupRepositoryAIProvider(GroupRepositoryGeneric[AIProviderOut, AIProvider]):
    def create(self, data: AIProviderCreate | dict):  # type: ignore[override]
        if isinstance(data, AIProviderCreate):
            api_key = data.api_key
            data = data.model_dump()
            data["api_key"] = api_key

        if not data.get("api_key"):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="API key cannot be empty")

        if not data.get("settings_id"):
            data["settings_id"] = _get_settings_id(self)

        return super().create(data)

    def update(self, match_value: str | int | UUID4, new_data: AIProviderCreate | dict):  # type: ignore[override]
        if not isinstance(new_data, AIProviderCreate):
            raise TypeError("AI provider updates must be an AIProviderCreate so resolve_update() checks the base URL")

        existing = self.get_one(match_value)
        if existing:
            new_data = existing.resolve_update(new_data)

        return super().update(match_value, new_data)

    def delete(self, value, match_key: str | None = None) -> AIProviderOut:
        # Null out any settings references to this provider before deleting
        self.session.execute(
            sa.update(AIProviderSettings)
            .where(AIProviderSettings.default_provider_id == value)
            .values(default_provider_id=None)
        )
        self.session.execute(
            sa.update(AIProviderSettings)
            .where(AIProviderSettings.audio_provider_id == value)
            .values(audio_provider_id=None)
        )
        self.session.execute(
            sa.update(AIProviderSettings)
            .where(AIProviderSettings.image_provider_id == value)
            .values(image_provider_id=None)
        )

        # Delete
        return super().delete(value, match_key)

    def update_many(self, data):
        raise NotImplementedError


class GroupRepositoryAIPromptOverride(GroupRepositoryGeneric[AIPromptOverrideOut, AIPromptOverride]):
    def create(self, data: AIPromptOverrideCreate | dict):  # type: ignore[override]
        if isinstance(data, AIPromptOverrideCreate):
            data = data.model_dump()

        if not data.get("settings_id"):
            data["settings_id"] = _get_settings_id(self)

        return super().create(data)
