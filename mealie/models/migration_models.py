from datetime import datetime

from pydantic.main import BaseModel


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
    files: list[MigrationFile] = []
