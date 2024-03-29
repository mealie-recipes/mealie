from pydantic import ConfigDict

from mealie.schema._mealie import MealieModel


class RecipeSettings(MealieModel):
    public: bool = False
    show_nutrition: bool = False
    show_assets: bool = False
    landscape_view: bool = False
    disable_comments: bool = True
    disable_amount: bool = True
    locked: bool = False
    model_config = ConfigDict(from_attributes=True)
