from __future__ import annotations

from mealie.core.root_logger import get_logger
from mealie.db.database import get_database
from mealie.schema.group import ReadWebhook
from mealie.schema.group.webhook import CreateWebhook, SaveWebhook
from mealie.services._base_http_service.crud_http_mixins import CrudHttpMixins
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_group_event

logger = get_logger(module=__name__)


class WebhookService(UserHttpService[int, ReadWebhook], CrudHttpMixins[ReadWebhook, CreateWebhook, CreateWebhook]):
    event_func = create_group_event
    _restrict_by_group = True

    _schema = ReadWebhook

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dal = get_database().webhooks

    def populate_item(self, id: int) -> ReadWebhook:
        self.item = self.db.webhooks.get_one(self.session, id)
        return self.item

    def get_all(self) -> list[ReadWebhook]:
        return self.db.webhooks.get(self.session, self.group_id, match_key="group_id", limit=9999)

    def create_one(self, data: CreateWebhook) -> ReadWebhook:
        data = self.cast(data, SaveWebhook)
        return self._create_one(data)

    def update_one(self, data: CreateWebhook, item_id: int = None) -> ReadWebhook:
        return self._update_one(data, item_id)

    def delete_one(self, id: int = None) -> ReadWebhook:
        return self._delete_one(id)
