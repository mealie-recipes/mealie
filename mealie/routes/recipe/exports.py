from shutil import rmtree

from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from mealie.core.dependencies import get_temporary_path
from mealie.routes._base import controller
from mealie.routes._base.routers import UserAPIRouter
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
