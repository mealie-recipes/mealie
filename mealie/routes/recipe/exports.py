from shutil import rmtree
from zipfile import ZipFile

from fastapi import (
    HTTPException,
)
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from mealie.core.dependencies import (
    get_temporary_path,
    get_temporary_zip_path,
    validate_recipe_token,
)
from mealie.core.security import create_recipe_slug_token
from mealie.routes._base import controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.recipe import Recipe, RecipeImageTypes
from mealie.schema.recipe.request_helpers import (
    RecipeZipTokenResponse,
)
from mealie.services.recipe.template_service import TemplateService

from ._base import BaseRecipeController, FormatResponse

router = UserAPIRouter(prefix="/recipes")


@controller(router)
class RecipeExportController(BaseRecipeController):
    # ==================================================================================================================
    # Export Operations

    @router.get("/exports", response_model=FormatResponse)
    def get_recipe_formats_and_templates(self):
        return TemplateService().templates

    @router.post("/{slug}/exports", response_model=RecipeZipTokenResponse)
    def get_recipe_zip_token(self, slug: str):
        """Generates a recipe zip token to be used to download a recipe as a zip file"""
        return RecipeZipTokenResponse(token=create_recipe_slug_token(slug))

    @router.get("/{slug}/exports", response_class=FileResponse)
    def get_recipe_as_format(self, slug: str, template_name: str):
        """
        ## Parameters
        `template_name`: The name of the template to use to use in the exports listed. Template type will automatically
        be set on the backend. Because of this, it's important that your templates have unique names. See available
        names and formats in the /api/recipes/exports endpoint.

        """
        with get_temporary_path(auto_unlink=False) as temp_path:
            recipe = self.mixins.get_one(slug)
            file = self.service.render_template(recipe, temp_path, template_name)
            return FileResponse(file, background=BackgroundTask(rmtree, temp_path))

    @router.get("/{slug}/exports/zip")
    def get_recipe_as_zip(self, slug: str, token: str):
        """Get a Recipe and Its Original Image as a Zip File"""
        with get_temporary_zip_path(auto_unlink=False) as temp_path:
            validated_slug = validate_recipe_token(token)

            if validated_slug != slug:
                raise HTTPException(status_code=400, detail="Invalid Slug")

            recipe: Recipe = self.mixins.get_one(validated_slug)
            image_asset = recipe.image_dir.joinpath(RecipeImageTypes.original.value)
            with ZipFile(temp_path, "w") as myzip:
                myzip.writestr(f"{slug}.json", recipe.model_dump_json())

                if image_asset.is_file():
                    myzip.write(image_asset, arcname=image_asset.name)

            return FileResponse(
                temp_path, filename=f"{recipe.slug}.zip", background=BackgroundTask(temp_path.unlink, missing_ok=True)
            )
