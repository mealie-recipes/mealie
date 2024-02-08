from mealie.schema._mealie import MealieModel
from pydantic import ConfigDict


class RecipeAsset(MealieModel):
    name: str
    icon: str
    file_name: str | None
    model_config = ConfigDict(from_attributes=True)
