from typing import Optional

from fastapi_camelcase import CamelModel

from schema.category import CategoryBase


class Sidebar(CamelModel):
    categories: Optional[list[CategoryBase]]

    class Config:
        orm_mode = True


class SiteSettings(CamelModel):
    language: str
    sidebar: Sidebar

    class Config:
        orm_mode = True

        schema_extra = {
            "example": {"id": "1", "language": "en", "sidebar": ["// TODO"]}
        }
