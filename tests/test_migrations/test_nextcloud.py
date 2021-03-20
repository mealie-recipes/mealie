from pathlib import Path

import pytest
from mealie.core.config import TEMP_DIR
from mealie.schema.recipe import Recipe
from mealie.services.image_services import IMG_DIR
from mealie.services.migrations.nextcloud import (
    cleanup,
    import_recipes,
    prep,
    process_selection,
)
from tests.test_config import TEST_NEXTCLOUD_DIR

CWD = Path(__file__).parent
TEST_NEXTCLOUD_DIR
TEMP_NEXTCLOUD = TEMP_DIR.joinpath("nextcloud")


@pytest.mark.parametrize(
    "file_name,final_path",
    [("nextcloud.zip", TEMP_NEXTCLOUD)],
)
def test_zip_extraction(file_name: str, final_path: Path):
    prep()
    zip = TEST_NEXTCLOUD_DIR.joinpath(file_name)
    dir = process_selection(zip)

    assert dir == final_path
    cleanup()
    assert dir.exists() == False


@pytest.mark.parametrize(
    "recipe_dir",
    [
        TEST_NEXTCLOUD_DIR.joinpath("Air Fryer Shrimp"),
        TEST_NEXTCLOUD_DIR.joinpath("Chicken Parmigiana"),
        TEST_NEXTCLOUD_DIR.joinpath("Skillet Shepherd's Pie"),
    ],
)
def test_nextcloud_migration(recipe_dir: Path):
    recipe = import_recipes(recipe_dir)
    assert isinstance(recipe, Recipe)
    IMG_DIR.joinpath(recipe.image).unlink(missing_ok=True)
