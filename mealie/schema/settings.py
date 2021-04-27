from typing import Optional

from fastapi_camelcase import CamelModel
from mealie.schema.category import CategoryBase
from pydantic import validator
from slugify import slugify


class SiteSettings(CamelModel):
    language: str = "en-US"
    first_day_of_week: int = 0
    show_recent: bool = True
    cards_per_section: int = 9
    categories: Optional[list[CategoryBase]] = []

    class Config:
        orm_mode = True

<<<<<<< HEAD
        schema_extra = {
            "example": {
                "language": "en",
                "firstDayOfWeek": 0,
                "showRecent": True,
                "categories": [
                    {"id": 1, "name": "thanksgiving", "slug": "thanksgiving"},
                    {"id": 2, "name": "homechef", "slug": "homechef"},
                    {"id": 3, "name": "potatoes", "slug": "potatoes"},
                ],
            }
        }

=======
>>>>>>> 0afdaf6 (Add alembic)

class CustomPageBase(CamelModel):
    name: str
    slug: Optional[str]
    position: int
    categories: list[CategoryBase] = []

    class Config:
        orm_mode = True

    @validator("slug", always=True, pre=True)
    def validate_slug(slug: str, values):
        name: str = values["name"]
        calc_slug: str = slugify(name)

        if slug != calc_slug:
            slug = calc_slug

        return slug


class CustomPageOut(CustomPageBase):
    id: int

    class Config:
        orm_mode = True
