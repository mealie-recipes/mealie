from uuid import UUID

from fastapi_camelcase import CamelModel


class CreateWebhook(CamelModel):
    enabled: bool = True
    name: str = ""
    url: str = ""
    time: str = "00:00"


class SaveWebhook(CreateWebhook):
    group_id: UUID


class ReadWebhook(SaveWebhook):
    id: int

    class Config:
        orm_mode = True
