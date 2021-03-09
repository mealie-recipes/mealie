from typing import Optional

from fastapi_camelcase import CamelModel

from schema.category import CategoryBase


class SiteSettings(CamelModel):
    language: str = "en"
    show_recent: bool = True
    categories: Optional[list[CategoryBase]] = []

    class Config:
        orm_mode = True

        schema_extra = {
            "example": {
                "language": "en",
                "showRecent": True,
                "categories": [
                    {"id": 1, "name": "thanksgiving", "slug": "thanksgiving"},
                    {"id": 2, "name": "homechef", "slug": "homechef"},
                    {"id": 3, "name": "potatoes", "slug": "potatoes"},
                ],
            }
        }
