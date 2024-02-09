from pydantic import ConfigDict

from mealie.schema._mealie import MealieModel


class RecipeAsset(MealieModel):
    name: str
    icon: str
    file_name: str | None = None
    model_config = ConfigDict(from_attributes=True)
