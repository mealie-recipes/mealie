from uuid import UUID

from pydantic import UUID4

from mealie.schema._mealie import MealieModel


class UpdateGroupPreferences(MealieModel):
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
