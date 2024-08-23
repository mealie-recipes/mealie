import tempfile
from pathlib import Path
from uuid import UUID

from mealie.schema.recipe.recipe import Recipe
from mealie.services.recipe.recipe_bulk_service import RecipeBulkActionsService
from mealie.services.scheduler.tasks.purge_group_exports import purge_group_data_exports
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


def test_purge_group_exports(unique_user: TestUser):
    database = unique_user.repos

    # create the export
    group = database.groups.get_one(unique_user.group_id)
    assert group
    user = database.users.get_one(unique_user.user_id)
    assert user
    recipe_exporter = RecipeBulkActionsService(database, user, group)
    recipes = [
        database.recipes.create(
            Recipe(
                name=random_string(),
                group_id=UUID(unique_user.group_id),
                user_id=unique_user.user_id,
            )
        )
        for _ in range(random_int(2, 5))
    ]

    with tempfile.NamedTemporaryFile() as tmpfile:
        recipe_exporter.export_recipes(Path(tmpfile.name), [recipe.slug for recipe in recipes])

    exports = recipe_exporter.get_exports()
    assert len(exports) == 1
    export = exports[0]
    export_path = Path(export.path)
    assert export_path.exists()

    # purge the export and confirm all data is removed
    purge_group_data_exports(-525600)  # 1 year into the future

    assert not export_path.exists()
    exports = recipe_exporter.get_exports()
    assert not exports
