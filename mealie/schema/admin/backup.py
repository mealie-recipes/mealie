from datetime import datetime

from pydantic import BaseModel


class BackupFile(BaseModel):
    name: str
    date: datetime
    size: str


class AllBackups(BaseModel):
    imports: list[BackupFile]
    templates: list[str]
