from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class BackupOptions(BaseModel):
    recipes: bool = True
    settings: bool = True
    themes: bool = True
    groups: bool = True
    users: bool = True
    notifications: bool = True

    class Config:
        schema_extra = {
            "example": {
                "recipes": True,
                "settings": True,
                "themes": True,
                "groups": True,
                "users": True,
            }
        }


class ImportJob(BackupOptions):
    name: str
    force: bool = False
    rebase: bool = False

    class Config:
        schema_extra = {
            "example": {
                "name": "my_local_backup.zip",
                "recipes": True,
                "settings": True,
                "themes": True,
                "groups": True,
                "users": True,
            }
        }


class CreateBackup(BaseModel):
    tag: Optional[str]
    options: BackupOptions
    templates: Optional[List[str]]

    class Config:
        schema_extra = {
            "example": {
                "tag": "July 23rd 2021",
                "options": BackupOptions(),
                "template": ["recipes.md"],
            }
        }


class BackupFile(BaseModel):
    name: str
    date: datetime


class AllBackups(BaseModel):
    imports: List[BackupFile]
    templates: List[str]

    class Config:
        schema_extra = {
            "example": {
                "imports": [
                    {
                        "name": "AutoBackup_12-1-2020.zip",
                        "date": datetime.now(),
                    }
                ],
                "templates": ["recipes.md", "custom_template.md"],
            }
        }
