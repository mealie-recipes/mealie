from uuid import UUID

from pydantic import UUID4

from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import PaginationBase


class CreateWebhook(MealieModel):
    enabled: bool = True
    name: str = ""
    url: str = ""
    time: str = "00:00"


class SaveWebhook(CreateWebhook):
    group_id: UUID


class ReadWebhook(SaveWebhook):
    id: UUID4

    class Config:
        orm_mode = True


class WebhookPagination(PaginationBase):
    data: list[ReadWebhook]
