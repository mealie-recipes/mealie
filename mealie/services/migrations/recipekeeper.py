import tempfile
import zipfile
from pathlib import Path

from bs4 import BeautifulSoup

from mealie.services.scraper import cleaner

from ._migration_base import BaseMigrator
from .utils.migration_alias import MigrationAlias
from .utils.migration_helpers import import_image, parse_iso8601_duration


def clean_instructions(instructions: list[str]) -> list[str]:
    try:
        for i, instruction in enumerate(instructions):
            if instruction.startswith(f"{i + 1}. "):
                instructions[i] = instruction.removeprefix(f"{i + 1}. ")

        return instructions
    except Exception:
        return instructions


def parse_recipe_div(recipe, image_path):
    meta = {}
    for item in recipe.find_all(lambda x: x.has_attr("itemprop")):
        if item.name == "meta":
            meta[item["itemprop"]] = item["content"]
        elif item.name == "div":
            meta[item["itemprop"]] = list(item.stripped_strings)
        elif item.name == "img":
            meta[item["itemprop"]] = str(image_path / item["src"])
        else:
            meta[item["itemprop"]] = item.string
    # merge nutrition keys into their own dict.
    nutrition = {}
    for k in meta:
        if k.startswith("recipeNut"):
            nutrition[k.removeprefix("recipeNut")] = meta[k].strip()
    meta["nutrition"] = nutrition
    return meta


def get_value_as_string_or_none(dictionary: dict, key: str):
    value = dictionary.get(key)
    if value is not None:
        try:
            return str(value)
        except Exception:
            return None
    else:
        return None


def to_list(x: list[str] | str) -> list[str]:
    if isinstance(x, str):
        return [x]
    return x


class RecipeKeeperMigrator(BaseMigrator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "recipekeeper"

        self.key_aliases = [
            MigrationAlias(
                key="recipeIngredient",
                alias="recipeIngredients",
            ),
            MigrationAlias(key="recipeInstructions", alias="recipeDirections", func=clean_instructions),
            MigrationAlias(key="performTime", alias="cookTime", func=parse_iso8601_duration),
            MigrationAlias(key="prepTime", alias="prepTime", func=parse_iso8601_duration),
            MigrationAlias(key="image", alias="photo0"),
            MigrationAlias(key="tags", alias="recipeCourse", func=to_list),
            MigrationAlias(key="recipe_category", alias="recipeCategory", func=to_list),
            MigrationAlias(key="notes", alias="recipeNotes"),
            MigrationAlias(key="nutrition", alias="nutrition", func=cleaner.clean_nutrition),
            MigrationAlias(key="rating", alias="recipeRating"),
            MigrationAlias(key="orgURL", alias="recipeSource"),
            MigrationAlias(key="recipe_yield", alias="recipeYield"),
        ]

    def _migrate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(self.archive) as zip_file:
                zip_file.extractall(tmpdir)

            source_dir = self.get_zip_base_path(Path(tmpdir))

            recipes_as_dicts: list[dict] = []
            with open(source_dir / "recipes.html") as fp:
                soup = BeautifulSoup(fp, "lxml")
                for recipe_div in soup.body.find_all("div", "recipe-details"):
                    recipes_as_dicts.append(parse_recipe_div(recipe_div, source_dir))

            recipes = [self.clean_recipe_dictionary(x) for x in recipes_as_dicts]
            results = self.import_recipes_to_database(recipes)
            for (_, recipe_id, status), recipe in zip(results, recipes, strict=False):
                if status:
                    try:
                        if not recipe or not recipe.image:
                            continue

                    except StopIteration:
                        continue

                    import_image(recipe.image, recipe_id)
