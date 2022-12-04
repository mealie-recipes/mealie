from mealie.schema._mealie import MealieModel


class RecipeAsset(MealieModel):
    name: str
    icon: str
    file_name: str | None

    class Config:
        orm_mode = True
