import datetime
import enum
from uuid import UUID

from pydantic import UUID4

from mealie.schema._mealie import MealieModel


class WebhookType(str, enum.Enum):
    mealplan = "mealplan"


class CreateWebhook(MealieModel):
    enabled: bool = True
    name: str = ""
    url: str = ""

    webhook_type: WebhookType = WebhookType.mealplan
    scheduled_time: datetime.time


class SaveWebhook(CreateWebhook):
    group_id: UUID


class ReadWebhook(SaveWebhook):
    id: UUID4

    class Config:
        orm_mode = True
