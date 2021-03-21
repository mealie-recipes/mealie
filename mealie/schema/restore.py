from typing import Optional

from pydantic.main import BaseModel


class ImportBase(BaseModel):
    name: str
    status: bool
    exception: Optional[str]


class RecipeImport(ImportBase):
    slug: str


class ThemeImport(ImportBase):
    pass


class SettingsImport(ImportBase):
    pass


class GroupImport(ImportBase):
    pass


class UserImport(ImportBase):
    pass
