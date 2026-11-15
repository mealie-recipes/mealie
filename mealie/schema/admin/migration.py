from datetime import datetime

from pydantic.main import BaseModel


class MigrationFile(BaseModel):
    name: str
    date: datetime


class Migrations(BaseModel):
    type: str
    files: list[MigrationFile] = []
