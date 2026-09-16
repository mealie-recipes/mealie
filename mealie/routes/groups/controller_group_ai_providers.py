from uuid import uuid4

from fastapi import APIRouter
from pydantic import UUID4

from mealie.core.root_logger import get_logger
from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.mixins import HttpRepo
from mealie.schema.group.ai_providers import (
    AIProviderCreate,
    AIProviderOut,
    AIProviderSettingsOut,
    AIProviderSettingsUpdate,
    AIProviderTestResult,
    AIProviderUpdate,
)
from mealie.services.openai import OpenAIService

logger = get_logger()
settings_router = APIRouter(prefix="/groups/ai-providers/settings", tags=["Groups: AI Provider Settings"])
providers_router = APIRouter(prefix="/groups/ai-providers/providers", tags=["Groups: AI Providers"])


@controller(settings_router)
class GroupAIProviderSettingsController(BaseUserController):
    @settings_router.get("", response_model=AIProviderSettingsOut)
    def get_ai_provider_settings(self) -> AIProviderSettingsOut:
        self.checks.can_manage()

        return self.repos.group_ai_provider_settings.get_one(self.group_id)

    @settings_router.put("", response_model=AIProviderSettingsOut)
    def update_ai_provider_settings(self, settings: AIProviderSettingsUpdate) -> AIProviderSettingsOut:
        self.checks.can_manage()

        return self.repos.group_ai_provider_settings.update(self.group_id, settings)


@controller(providers_router)
class GroupAIProviderController(BaseUserController):
    @property
    def mixins(self):
        return HttpRepo[AIProviderCreate, AIProviderOut, AIProviderUpdate](self.repos.group_ai_providers, self.logger)

    @providers_router.post("", response_model=AIProviderOut)
    def create_ai_provider(self, data: AIProviderCreate) -> AIProviderOut:
        self.checks.can_manage()

        return self.mixins.create_one(data)

    @providers_router.post("/test", response_model=AIProviderTestResult)
    async def test_ai_provider(self, data: AIProviderCreate) -> AIProviderTestResult:
        """Test connectivity for a provider configuration before it has been saved."""
        self.checks.can_manage()

        # Ephemeral provider, never persisted or looked up by this id
        provider = AIProviderOut(
            id=uuid4(),
            name=data.name,
            base_url=data.base_url,
            api_key=data.api_key,
            model=data.model,
            timeout=data.timeout,
            request_headers=data.request_headers,
            request_params=data.request_params,
        )
        return await OpenAIService(self.repos).test_connection(provider)

    @providers_router.post("/{provider_id}/test", response_model=AIProviderTestResult)
    async def test_saved_ai_provider(
        self, provider_id: UUID4, overrides: AIProviderUpdate | None = None
    ) -> AIProviderTestResult:
        """
        Test connectivity for an already-saved provider.

        Accepts optional unsaved edits to test against instead of what's in the database - e.g.
        while editing a provider, the caller may have changed the model/base_url but left the API
        key blank (meaning "keep the existing one"), so a plain "unsaved" test can't be used since
        it has no way to supply that key. An `overrides.apiKey` of "" is treated the same way: keep
        the saved key rather than testing with an empty one.
        """
        self.checks.can_manage()

        provider = self.mixins.get_one(provider_id)
        if overrides:
            provider = provider.model_copy(
                update={
                    "name": overrides.name,
                    "base_url": overrides.base_url,
                    "model": overrides.model,
                    "timeout": overrides.timeout,
                    "request_headers": overrides.request_headers,
                    "request_params": overrides.request_params,
                    **({"api_key": overrides.api_key} if overrides.api_key else {}),
                }
            )
        return await OpenAIService(self.repos).test_connection(provider)

    @providers_router.get("/{provider_id}", response_model=AIProviderOut)
    def get_ai_provider(self, provider_id: UUID4) -> AIProviderOut:
        self.checks.can_manage()

        return self.mixins.get_one(provider_id)

    @providers_router.put("/{provider_id}", response_model=AIProviderOut)
    def update_ai_provider(self, provider_id: UUID4, data: AIProviderUpdate) -> AIProviderOut:
        self.checks.can_manage()

        return self.mixins.update_one(data, provider_id)

    @providers_router.delete("/{provider_id}", response_model=AIProviderOut)
    def delete_ai_provider(self, provider_id: UUID4) -> AIProviderOut:
        self.checks.can_manage()

        return self.mixins.delete_one(provider_id)
