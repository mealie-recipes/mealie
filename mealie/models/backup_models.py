# from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class BackupJob(BaseModel):
    tag: Optional[str]
    template: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "tag": "July 23rd 2021",
                "template": "recipes.md",
            }
        }


class Imports(BaseModel):
    imports: List[str]
    templates: List[str]

    class Config:
        schema_extra = {
            "example": {
                "imports": ["sample_data.zip", "sampe_data2.zip"],
                "templates": ["recipes.md", "custom_template.md"],
            }
        }
