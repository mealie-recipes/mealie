from pydantic import BaseModel


class WebhookJob(BaseModel):
    webhook_urls: list[str] = []
    webhook_time: str = "00:00"
    webhook_enable: bool

    class Config:
        orm_mode = True
