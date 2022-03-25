from datetime import datetime

from pydantic import UUID4

from mealie.schema._mealie import MealieModel


class GroupDataExport(MealieModel):
    id: UUID4
    group_id: UUID4
    name: str
    filename: str
    path: str
    size: str
    expires: datetime

    class Config:
        orm_mode = True
