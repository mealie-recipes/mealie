from fastapi_camelcase import CamelModel


class CreateGroupPreferences(CamelModel):
    group_id: int
    private_group: bool = False
    first_day_of_week: int = 0

    # Recipe Defaults
    recipe_public: bool = True
    recipe_show_nutrition: bool = False
    recipe_show_assets: bool = False
    recipe_landscape_view: bool = False
    recipe_disable_comments: bool = False
    recipe_disable_amount: bool = False

    class Config:
        orm_mode = True


class ReadGroupPreferences(CreateGroupPreferences):
    id: int

    class Config:
        orm_mode = True
