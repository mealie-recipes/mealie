import datetime
import enum
from uuid import UUID

from isodate import parse_time
from pydantic import UUID4, validator
from pydantic.datetime_parse import parse_datetime

from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import PaginationBase


class WebhookType(str, enum.Enum):
    mealplan = "mealplan"


class CreateWebhook(MealieModel):
    enabled: bool = True
    name: str = ""
    url: str = ""

    webhook_type: WebhookType = WebhookType.mealplan
    scheduled_time: datetime.time

    @validator("scheduled_time", pre=True)
    @classmethod
    def validate_scheduled_time(cls, v):
        """
        Validator accepts both datetime and time values from external sources.
        DateTime types are parsed and converted to time objects without timezones

        type: time is treated as a UTC value
        type: datetime is treated as a value with a timezone
        """
        parser_funcs = [
            lambda x: parse_datetime(x).astimezone(datetime.timezone.utc).time(),
            parse_time,
        ]

        if isinstance(v, datetime.time):
            return v

        for parser_func in parser_funcs:
            try:
                return parser_func(v)
            except ValueError:
                continue

        raise ValueError(f"Invalid scheduled time: {v}")


class SaveWebhook(CreateWebhook):
    group_id: UUID


class ReadWebhook(SaveWebhook):
    id: UUID4

    class Config:
        orm_mode = True


class WebhookPagination(PaginationBase):
    items: list[ReadWebhook]
