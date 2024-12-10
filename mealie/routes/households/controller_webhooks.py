from datetime import UTC, datetime
from functools import cached_property

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import UUID4

from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema import mapper
from mealie.schema.household.webhook import CreateWebhook, ReadWebhook, SaveWebhook, WebhookPagination
from mealie.schema.response.pagination import PaginationQuery
from mealie.services.scheduler.tasks.post_webhooks import post_group_webhooks, post_single_webhook

router = APIRouter(prefix="/households/webhooks", tags=["Households: Webhooks"])


@controller(router)
class ReadWebhookController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.webhooks

    @property
    def mixins(self) -> HttpRepo:
        return HttpRepo[CreateWebhook, SaveWebhook, CreateWebhook](self.repo, self.logger)

    @router.get("", response_model=WebhookPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repo.page_all(
            pagination=q,
            override=ReadWebhook,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=ReadWebhook, status_code=201)
    def create_one(self, data: CreateWebhook):
        save = mapper.cast(data, SaveWebhook, group_id=self.group_id, household_id=self.household_id)
        return self.mixins.create_one(save)

    @router.post("/rerun")
    def rerun_webhooks(self):
        """Manually re-fires all previously scheduled webhooks for today"""

        start_time = datetime.min.time()
        start_dt = datetime.combine(datetime.now(UTC).date(), start_time)
        post_group_webhooks(start_dt=start_dt, group_id=self.group.id, household_id=self.household.id)

    @router.get("/{item_id}", response_model=ReadWebhook)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.post("/{item_id}/test")
    def test_one(self, item_id: UUID4, bg_tasks: BackgroundTasks):
        webhook = self.mixins.get_one(item_id)
        bg_tasks.add_task(post_single_webhook, webhook, "Test Webhook")

    @router.put("/{item_id}", response_model=ReadWebhook)
    def update_one(self, item_id: UUID4, data: CreateWebhook):
        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=ReadWebhook)
    def delete_one(self, item_id: UUID4):
        return self.mixins.delete_one(item_id)  # type: ignore
