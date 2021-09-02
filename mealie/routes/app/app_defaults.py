from fastapi import APIRouter

from mealie.schema.recipe.recipe_settings import RecipeSettings

router = APIRouter(prefix="/defaults")


@router.get("/recipe", response_model=RecipeSettings)
async def get_recipe_settings_defaults():
    """ Returns the Default Settings for Recieps as set by ENV variables """

    return RecipeSettings()
