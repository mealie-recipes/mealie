from datetime import datetime

from pydantic import BaseModel


class BackupOptions(BaseModel):
    recipes: bool = True
    settings: bool = True
    themes: bool = True
    groups: bool = True
    users: bool = True
    notifications: bool = True


class ImportJob(BackupOptions):
    name: str
    force: bool = False
    rebase: bool = False


class CreateBackup(BaseModel):
    tag: str | None = None
    options: BackupOptions
    templates: list[str] | None = None


class BackupFile(BaseModel):
    name: str
    date: datetime
    size: str


class AllBackups(BaseModel):
    imports: list[BackupFile]
    templates: list[str]
