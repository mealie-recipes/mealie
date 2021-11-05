from zipfile import ZipFile

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm.session import Session
from starlette.responses import FileResponse

from mealie.core.dependencies import temporary_zip_path
from mealie.core.dependencies.dependencies import temporary_dir, validate_recipe_token
from mealie.core.root_logger import get_logger
from mealie.core.security import create_recipe_slug_token
from mealie.db.database import get_database
from mealie.db.db_setup import generate_session
from mealie.routes.routers import UserAPIRouter
from mealie.schema.recipe import Recipe, RecipeImageTypes
from mealie.services.recipe.recipe_service import RecipeService
from mealie.services.recipe.template_service import TemplateService

user_router = UserAPIRouter()
public_router = APIRouter()
logger = get_logger()


class FormatResponse(BaseModel):
    jjson: list[str] = Field(..., alias="json")
    zip: list[str]
    jinja2: list[str]


@user_router.get("/exports", response_model=FormatResponse)
async def get_recipe_formats_and_templates(_: RecipeService = Depends(RecipeService.private)):
    return TemplateService().templates


@user_router.post("/{slug}/exports")
async def get_recipe_zip_token(slug: str):
    """ Generates a recipe zip token to be used to download a recipe as a zip file """
    return {"token": create_recipe_slug_token(slug)}


@user_router.get("/{slug}/exports", response_class=FileResponse)
def get_recipe_as_format(
    template_name: str,
    recipe_service: RecipeService = Depends(RecipeService.write_existing),
    temp_dir=Depends(temporary_dir),
):
    """
    ## Parameters
    `template_name`: The name of the template to use to use in the exports listed. Template type will automatically
    be set on the backend. Because of this, it's important that your templates have unique names. See available
    names and formats in the /api/recipes/exports endpoint.

    """
    file = recipe_service.render_template(temp_dir, template_name)
    return FileResponse(file)


@public_router.get("/{slug}/exports/zip")
async def get_recipe_as_zip(
    token: str,
    slug: str,
    session: Session = Depends(generate_session),
    temp_path=Depends(temporary_zip_path),
):
    """ Get a Recipe and It's Original Image as a Zip File """
    slug = validate_recipe_token(token)

    if slug != slug:
        raise HTTPException(status_code=400, detail="Invalid Slug")

    db = get_database(session)
    recipe: Recipe = db.recipes.get(slug)
    image_asset = recipe.image_dir.joinpath(RecipeImageTypes.original.value)
    with ZipFile(temp_path, "w") as myzip:
        myzip.writestr(f"{slug}.json", recipe.json())

        if image_asset.is_file():
            myzip.write(image_asset, arcname=image_asset.name)

    return FileResponse(temp_path, filename=f"{slug}.zip")
