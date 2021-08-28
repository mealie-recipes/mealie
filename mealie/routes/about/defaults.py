from fastapi import APIRouter

from mealie.schema.recipe import RecipeSettings

router = APIRouter(prefix="/recipes")


@router.get("/defaults")
async def get_recipe_settings_defaults():
    """ Returns the Default Settings for Recieps as set by ENV variables """

    return RecipeSettings()
