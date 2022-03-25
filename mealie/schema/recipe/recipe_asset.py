from typing import Optional

from mealie.schema._mealie import MealieModel


class RecipeAsset(MealieModel):
    name: str
    icon: str
    file_name: Optional[str]

    class Config:
        orm_mode = True
