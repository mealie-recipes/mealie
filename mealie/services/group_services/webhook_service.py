from __future__ import annotations

from fastapi import HTTPException, status

from mealie.core.root_logger import get_logger
from mealie.schema.group import ReadWebhook
from mealie.schema.group.webhook import CreateWebhook, SaveWebhook
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_group_event

logger = get_logger(module=__name__)


class WebhookService(UserHttpService[int, ReadWebhook]):
    event_func = create_group_event
    _restrict_by_group = True

    _schema = ReadWebhook
    _create_schema = CreateWebhook
    _update_schema = CreateWebhook

    def populate_item(self, id: int) -> ReadWebhook:
        self.item = self.db.webhooks.get_one(self.session, id)
        return self.item

    def get_all(self) -> list[ReadWebhook]:
        return self.db.webhooks.get(self.session, self.group_id, match_key="group_id", limit=9999)

    def create_one(self, data: CreateWebhook) -> ReadWebhook:
        try:
            self.item = self.db.webhooks.create(self.session, SaveWebhook(group_id=self.group_id, **data.dict()))
        except Exception as ex:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail={"message": "WEBHOOK_CREATION_ERROR", "exception": str(ex)}
            )

        return self.item

    def update_one(self, data: CreateWebhook, id: int = None) -> ReadWebhook:
        if not self.item:
            return

        target_id = id or self.item.id
        self.item = self.db.webhooks.update(self.session, target_id, data)

        return self.item

    def delete_one(self, id: int = None) -> ReadWebhook:
        if not self.item:
            return

        target_id = id or self.item.id
        self.db.webhooks.delete(self.session, target_id)

        return self.item
