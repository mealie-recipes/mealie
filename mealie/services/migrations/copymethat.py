import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from bs4 import BeautifulSoup

from mealie.schema.reports.reports import ReportEntryCreate

from ._migration_base import BaseMigrator
from .utils.migration_alias import MigrationAlias
from .utils.migration_helpers import import_image


def parse_recipe_tags(tags: list) -> list[str]:
    """Parses the list of recipe tags and removes invalid ones"""

    updated_tags: list[str] = []
    for tag in tags:
        if not tag or not isinstance(tag, str):
            continue

        if "Tags:" in tag:
            continue

        updated_tags.append(tag)

    return updated_tags


class CopyMeThatMigrator(BaseMigrator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "copymethat"

        self.key_aliases = [
            MigrationAlias(key="last_made", alias="made_this", func=lambda x: datetime.now(UTC)),
            MigrationAlias(key="notes", alias="recipeNotes"),
            MigrationAlias(key="orgURL", alias="original_link"),
            MigrationAlias(key="rating", alias="ratingValue"),
            MigrationAlias(key="recipeIngredient", alias="recipeIngredients"),
            MigrationAlias(key="recipeYield", alias="servings", func=lambda x: x.replace(":", ": ")),
        ]

    def _process_recipe_document(self, source_dir: Path, soup: BeautifulSoup) -> dict:
        """Reads a single recipe's HTML and converts it to a dictionary"""

        recipe_dict: dict = {}
        recipe_tags: list[str] = []
        for tag in soup.find_all():
            # the recipe image tag has no id, so we parse it directly
            if tag.name == "img" and "recipeImage" in tag.get("class", []):
                if image_path := tag.get("src"):
                    recipe_dict["image"] = str(source_dir.joinpath(image_path))

                continue

            # tags (internally named categories) are not in a list, and don't have ids
            if tag.name == "span" and "recipeCategory" in tag.get("class", []):
                recipe_tag = tag.get_text(strip=True)
                if "Tags:" not in recipe_tag:
                    recipe_tags.append(recipe_tag)

                continue

            # add only elements with an id to the recipe dictionary
            if not (tag_id := tag.get("id")):
                continue

            # for lists, store the list items as an array (e.g. for recipe instructions)
            if tag.name in ["ul", "ol"]:
                recipe_dict[tag_id] = [item.get_text(strip=True) for item in tag.find_all("li", recursive=False)]
                continue

            # for all other tags, write the text directly to the recipe data
            recipe_dict[tag_id] = tag.get_text(strip=True)

        if recipe_tags:
            recipe_dict["tags"] = recipe_tags

        return recipe_dict

    def _migrate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(self.archive) as zip_file:
                zip_file.extractall(tmpdir)

            source_dir = self.get_zip_base_path(Path(tmpdir))

            recipes_as_dicts: list[dict] = []
            for recipes_data_file in source_dir.glob("*.html"):
                with open(recipes_data_file, encoding="utf-8") as f:
                    soup = BeautifulSoup(f, "lxml")
                    for recipe_data in soup.find_all("div", class_="recipe"):
                        try:
                            recipes_as_dicts.append(self._process_recipe_document(source_dir, recipe_data))

                        # since recipes are stored in one large file, we keep going on error
                        except Exception as e:
                            self.report_entries.append(
                                ReportEntryCreate(
                                    report_id=self.report_id,
                                    success=False,
                                    message="Failed to parse recipe",
                                    exception=f"{type(e).__name__}: {e}",
                                )
                            )

            recipes = [self.clean_recipe_dictionary(x) for x in recipes_as_dicts]
            results = self.import_recipes_to_database(recipes)
            recipe_lookup = {r.slug: r for r in recipes}
            for slug, recipe_id, status in results:
                if status:
                    try:
                        r = recipe_lookup.get(slug)
                        if not r or not r.image:
                            continue

                    except StopIteration:
                        continue

                    import_image(r.image, recipe_id)
