from typing import List, Optional

from pydantic import BaseModel


class Webhooks(BaseModel):
    webhookTime: str = "00:00"
    webhookURLs: Optional[List[str]] = []
    enabled: bool = False


class SiteSettings(BaseModel):
    name: str = "main"
    planCategories: list[str] = []
    webhooks: Webhooks

    class Config:
        schema_extra = {
            "example": {
                "name": "main",
                "planCategories": ["dinner", "lunch"],
                "webhooks": {
                    "webhookTime": "00:00",
                    "webhookURLs": ["https://mywebhookurl.com/webhook"],
                    "enable": False,
                },
            }
        }
