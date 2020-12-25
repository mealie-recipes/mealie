# from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BackupJob(BaseModel):
    tag: Optional[str]
    template: Optional[str]
