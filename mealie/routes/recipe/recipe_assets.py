import shutil

from fastapi import APIRouter, Depends, File, Form
from fastapi.datastructures import UploadFile
from fastapi.routing import run_endpoint_function
from mealie.core.config import app_dirs
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.schema.recipe import Recipe, RecipeAsset
from mealie.schema.snackbar import SnackResponse
from slugify import slugify
from sqlalchemy.orm.session import Session
from starlette.responses import FileResponse

router = APIRouter(prefix="/api/recipes", tags=["Recipe Assets"])


@router.get("/{recipe_slug}/asset")
async def get_recipe_asset(recipe_slug, file_name: str):
    """ Returns a recipe asset """
    file = app_dirs.RECIPE_DATA_DIR.joinpath(recipe_slug, file_name)

    return FileResponse(file)


@router.post("/{recipe_slug}/asset", response_model=RecipeAsset)
def upload_recipe_asset(
    recipe_slug: str,
    name: str = Form(...),
    icon: str = Form(...),
    extension: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(generate_session),
    current_user=Depends(get_current_user),
):
    """ Upload a file to store as a recipe asset """
    file_name = slugify(name) + "." + extension
    asset_in = RecipeAsset(name=name, icon=icon, file_name=file_name)
    dest = app_dirs.RECIPE_DATA_DIR.joinpath(recipe_slug, file_name)
    dest.parent.mkdir(exist_ok=True, parents=True)

    with dest.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if dest.is_file():
        recipe: Recipe = db.recipes.get(session, recipe_slug)
        recipe.assets.append(asset_in)
        db.recipes.update(session, recipe_slug, recipe.dict())
        return asset_in
    else:
        return SnackResponse.error("Failure uploading file")
