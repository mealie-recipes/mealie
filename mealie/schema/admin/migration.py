from datetime import datetime
from typing import List

from pydantic.main import BaseModel

from .restore import RecipeImport


class ChowdownURL(BaseModel):
    url: str

    class Config:
        schema_extra = {
            "example": {
                "url": "https://chowdownrepo.com/repo",
            }
        }


class MigrationFile(BaseModel):
    name: str
    date: datetime


class Migrations(BaseModel):
    type: str
    files: List[MigrationFile] = []


class MigrationImport(RecipeImport):
    pass
