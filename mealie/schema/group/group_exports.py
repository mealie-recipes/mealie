from datetime import datetime

from fastapi_camelcase import CamelModel
from pydantic import UUID4


class GroupDataExport(CamelModel):
    id: UUID4
    group_id: UUID4
    name: str
    filename: str
    path: str
    size: str
    expires: datetime

    class Config:
        orm_mode = True
