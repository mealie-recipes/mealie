from fastapi_camelcase import CamelModel

from mealie.core.config import get_app_settings

settings = get_app_settings()


class RecipeSettings(CamelModel):
    public: bool = False
    show_nutrition: bool = False
    show_assets: bool = False
    landscape_view: bool = False
    disable_comments: bool = True
    disable_amount: bool = True

    class Config:
        orm_mode = True
