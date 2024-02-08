from datetime import datetime

from pydantic import ConfigDict, UUID4

from mealie.schema._mealie import MealieModel


class GroupDataExport(MealieModel):
    id: UUID4
    group_id: UUID4
    name: str
    filename: str
    path: str
    size: str
    expires: datetime
    model_config = ConfigDict(from_attributes=True)
