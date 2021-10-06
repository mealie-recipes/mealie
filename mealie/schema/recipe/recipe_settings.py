from fastapi_camelcase import CamelModel

from mealie.core.config import get_settings

settings = get_settings()


class RecipeSettings(CamelModel):
    public: bool = settings.RECIPE_PUBLIC
    show_nutrition: bool = settings.RECIPE_SHOW_NUTRITION
    show_assets: bool = settings.RECIPE_SHOW_ASSETS
    landscape_view: bool = settings.RECIPE_LANDSCAPE_VIEW
    disable_comments: bool = settings.RECIPE_DISABLE_COMMENTS
    disable_amount: bool = settings.RECIPE_DISABLE_AMOUNT

    class Config:
        orm_mode = True
