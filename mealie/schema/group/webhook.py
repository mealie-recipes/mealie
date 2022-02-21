from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import UUID4


class CreateWebhook(CamelModel):
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
