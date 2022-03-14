from datetime import datetime

from pydantic.main import BaseModel

from .restore import RecipeImport


class ChowdownURL(BaseModel):
    url: str


class MigrationFile(BaseModel):
    name: str
    date: datetime


class Migrations(BaseModel):
    type: str
    files: list[MigrationFile] = []


class MigrationImport(RecipeImport):
    pass
