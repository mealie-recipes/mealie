from pathlib import Path
from app_config import TEMP_DIR
import pytest
from services.image_services import IMG_DIR
from services.migrations.nextcloud import (
    cleanup,
    import_recipes,
    prep,
    process_selection,
)
from services.recipe_services import Recipe

CWD = Path(__file__).parent
NEXTCLOUD_DIR = CWD.joinpath("data", "nextcloud_recipes")
TEMP_NEXTCLOUD = TEMP_DIR.joinpath("nextcloud")


@pytest.mark.parametrize(
    "file_name,final_path",
    [("nextcloud.zip", TEMP_NEXTCLOUD)],
)
def test_zip_extraction(file_name: str, final_path: Path):
    prep()
    zip = NEXTCLOUD_DIR.joinpath(file_name)
    dir = process_selection(zip)

    assert dir == final_path
    cleanup()
    assert dir.exists() == False


@pytest.mark.parametrize(
    "recipe_dir",
    [
        NEXTCLOUD_DIR.joinpath("Air Fryer Shrimp"),
        NEXTCLOUD_DIR.joinpath("Chicken Parmigiana"),
        NEXTCLOUD_DIR.joinpath("Skillet Shepherd's Pie"),
    ],
)
def test_nextcloud_migration(recipe_dir: Path):
    recipe = import_recipes(recipe_dir)
    assert isinstance(recipe, Recipe)
    IMG_DIR.joinpath(recipe.image).unlink(missing_ok=True)
