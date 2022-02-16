from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import UUID4


class UpdateGroupPreferences(CamelModel):
    private_group: bool = False
    first_day_of_week: int = 0

    # Recipe Defaults
    recipe_public: bool = True
    recipe_show_nutrition: bool = False
    recipe_show_assets: bool = False
    recipe_landscape_view: bool = False
    recipe_disable_comments: bool = False
    recipe_disable_amount: bool = False


class CreateGroupPreferences(UpdateGroupPreferences):
    group_id: UUID


class ReadGroupPreferences(CreateGroupPreferences):
    id: UUID4

    class Config:
        orm_mode = True
