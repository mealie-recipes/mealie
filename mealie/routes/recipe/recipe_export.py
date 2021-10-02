from fastapi import Depends
from pydantic import BaseModel, Field
from starlette.responses import FileResponse

from mealie.core.dependencies.dependencies import temporary_dir
from mealie.core.root_logger import get_logger
from mealie.routes.routers import UserAPIRouter
from mealie.services.recipe.recipe_service import RecipeService
from mealie.services.recipe.template_service import TemplateService

user_router = UserAPIRouter()
logger = get_logger()


class FormatResponse(BaseModel):
    jjson: list[str] = Field(..., alias="json")
    zip: list[str]
    jinja2: list[str]


@user_router.get("/exports", response_model=FormatResponse)
async def get_recipe_formats_and_templates(_: RecipeService = Depends(RecipeService.private)):
    return TemplateService().templates


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
