from typing import Optional

from fastapi_camelcase import CamelModel
from mealie.schema.category import CategoryBase, RecipeCategoryResponse
from pydantic import validator
from slugify import slugify

# Cluge Validator for ISSUE: #671
langs = {
    "el-GR",
    "it-IT",
    "ko-KR",
    "es-ES",
    "ja-JP",
    "zh-CN",
    "tr-TR",
    "ar-SA",
    "hu-HU",
    "pt-PT",
    "no-NO",
    "sv-SE",
    "ro-RO",
    "sk-SK",
    "uk-UA",
    "pl-PL",
    "da-DK",
    "pt-BR",
    "de-DE",
    "ca-ES",
    "sr-SP",
    "cs-CZ",
    "fr-FR",
    "zh-TW",
    "af-ZA",
    "ru-RU",
    "he-IL",
    "nl-NL",
    "en-US",
    "en-GB",
    "fi-FI",
    "vi-VN",
}


class SiteSettings(CamelModel):
    language: str = "en-US"
    first_day_of_week: int = 0
    show_recent: bool = True
    cards_per_section: int = 9
    categories: Optional[list[CategoryBase]] = []

    class Config:
        orm_mode = True

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

    @validator("language")
    def language_validator(cls, v: str):
        if v not in langs:
            return "en-US"
        return v


class CustomPageBase(CamelModel):
    name: str
    slug: Optional[str]
    position: int
    categories: list[RecipeCategoryResponse] = []

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
