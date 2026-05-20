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
    AIProviderUpdate,
)

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
