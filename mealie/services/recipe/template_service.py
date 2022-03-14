import enum
from pathlib import Path
from zipfile import ZipFile

from jinja2 import Template

from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe_image_types import RecipeImageTypes
from mealie.services._base_service import BaseService


class TemplateType(str, enum.Enum):
    json = "json"
    jinja2 = "jinja2"
    zip = "zip"


class TemplateService(BaseService):
    def __init__(self, temp: Path = None) -> None:
        """Creates a template service that can be used for multiple template generations
        A temporary directory must be provided as a place holder for where to render all templates
        Args:
            temp (Path): [description]
        """
        self.temp = temp
        self.types = TemplateType
        super().__init__()

    @property
    def templates(self) -> dict[str, list[str]]:
        """
        Returns a list of all templates available to render.
        """
        return {
            TemplateType.jinja2.value: [x.name for x in self.directories.TEMPLATE_DIR.iterdir() if x.is_file()],
            TemplateType.json.value: ["raw"],
            TemplateType.zip.value: ["zip"],
        }

    def __check_temp(self, method) -> None:
        """
        Checks if the temporary directory was provided on initialization
        """

        if self.temp is None:
            raise ValueError(f"Temporary directory must be provided for method {method.__name__}")

    def template_type(self, template: str) -> TemplateType:
        # Determine Type:
        t_type = None
        for key, value in self.templates.items():
            if template in value:
                t_type = key
                break

        if t_type is None:
            raise ValueError(f"Template '{template}' not found.")

        return TemplateType(t_type)

    def render(self, recipe: Recipe, template: str = None) -> Path:
        """
        Renders a TemplateType in a temporary directory and returns the path to the file.

        Args:
            t_type (TemplateType): The type of template to render
            recipe (Recipe): The recipe to render
            template (str): The template to render **Required for Jinja2 Templates**
        """
        t_type = self.template_type(template)

        if t_type == TemplateType.json:
            return self._render_json(recipe)

        if t_type == TemplateType.jinja2:
            return self._render_jinja2(recipe, template)

        if t_type == TemplateType.zip:
            return self._render_zip(recipe)

        raise ValueError(f"Template Type '{t_type}' not found.")

    def _render_json(self, recipe: Recipe) -> Path:
        """
        Renders a JSON file in a temporary directory and returns
        the path to the file.
        """
        self.__check_temp(self._render_json)

        save_path = self.temp.joinpath(f"{recipe.slug}.json")
        with open(save_path, "w") as f:
            f.write(recipe.json(indent=4, by_alias=True))

        return save_path

    def _render_jinja2(self, recipe: Recipe, j2_template: str = None) -> Path:
        """
        Renders a Jinja2 Template in a temporary directory and returns
        the path to the file.
        """
        self.__check_temp(self._render_jinja2)

        j2_path: Path = self.directories.TEMPLATE_DIR / j2_template

        if not j2_path.is_file():
            raise FileNotFoundError(f"Template '{j2_path}' not found.")

        with open(j2_path, "r") as f:
            template_text = f.read()

        template = Template(template_text)
        rendered_text = template.render(recipe=recipe.dict(by_alias=True))

        save_name = f"{recipe.slug}{j2_path.suffix}"

        save_path = self.temp.joinpath(save_name)

        with open(save_path, "w") as f:
            f.write(rendered_text)

        return save_path

    def _render_zip(self, recipe: Recipe) -> Path:
        self.__check_temp(self._render_jinja2)

        image_asset = recipe.image_dir.joinpath(RecipeImageTypes.original.value)
        zip_temp = self.temp.joinpath(f"{recipe.slug}.zip")

        with ZipFile(zip_temp, "w") as myzip:
            myzip.writestr(f"{recipe.slug}.json", recipe.json())

            if image_asset.is_file():
                myzip.write(image_asset, arcname=image_asset.name)

        return zip_temp
