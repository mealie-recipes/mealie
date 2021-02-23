from typing import Optional

from pydantic.main import BaseModel


class RecipeImport(BaseModel):
    name: Optional[str]
    slug: str
    status: bool
    exception: Optional[str]

class ThemeImport(BaseModel):
    name: str
    status: bool
    exception: Optional[str]

class SettingsImport(BaseModel):
    name: str
    status: bool
    exception: Optional[str]