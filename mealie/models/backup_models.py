from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class BackupJob(BaseModel):
    tag: Optional[str]
    template: Optional[List[str]]

    class Config:
        schema_extra = {
            "example": {
                "tag": "July 23rd 2021",
                "template": "recipes.md",
            }
        }


class LocalBackup(BaseModel):
    name: str
    date: datetime


class Imports(BaseModel):
    imports: List[LocalBackup]
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


class ImportJob(BaseModel):
    name: str
    recipes: bool
    force: bool = False
    rebase: bool = False
    themes: bool = False
    settings: bool = False

    class Config:
            schema_extra = {
                "example": {
                    "name": "my_local_backup.zip",
                    "recipes": True,
                    "force": False,
                    "rebase": False,
                    "themes": False,
                    "settings": False
                }
            }
