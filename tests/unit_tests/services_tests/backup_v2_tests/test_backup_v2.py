import filecmp
import statistics
from pathlib import Path
from typing import Any, cast

import pytest
from sqlalchemy.orm import Session

import tests.data as test_data
from mealie.core.config import get_app_settings
from mealie.db.db_setup import session_context
from mealie.db.models._model_utils.guid import GUID
from mealie.db.models.group import Group
from mealie.db.models.household.cookbook import CookBook
from mealie.db.models.household.mealplan import GroupMealPlanRules
from mealie.db.models.household.shopping_list import ShoppingList
from mealie.db.models.labels import MultiPurposeLabel
from mealie.db.models.recipe.ingredient import IngredientFoodModel, IngredientUnitModel
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.users.user_to_recipe import UserToRecipe
from mealie.db.models.users.users import User
from mealie.services.backups_v2.alchemy_exporter import AlchemyExporter
from mealie.services.backups_v2.backup_file import BackupFile
from mealie.services.backups_v2.backup_v2 import BackupV2


def dict_sorter(d: dict) -> Any:
    possible_keys = {"created_at", "id"}

    return next((d[key] for key in possible_keys if d.get(key)), 1)


# For Future Use
def match_file_tree(path_a: Path, path_b: Path):
    if path_a.is_dir() and path_b.is_dir():
        for a_file in path_a.iterdir():
            b_file = path_b.joinpath(a_file.name)
            assert b_file.exists()
            match_file_tree(a_file, b_file)
    else:
        assert filecmp.cmp(path_a, path_b)


def test_database_backup():
    backup_v2 = BackupV2()
    path_to_backup = backup_v2.backup()

    assert path_to_backup.exists()

    backup = BackupFile(path_to_backup)

    with backup as contents:
        assert contents.validate()


def test_database_restore():
    settings = get_app_settings()

    # Capture existing database snapshot
    original_exporter = AlchemyExporter(settings.DB_URL)
    snapshop_1 = original_exporter.dump()

    # Create Backup
    backup_v2 = BackupV2(settings.DB_URL)
    path_to_backup = backup_v2.backup()

    assert path_to_backup.exists()
    backup_v2.restore(path_to_backup)

    new_exporter = AlchemyExporter(settings.DB_URL)
    snapshop_2 = new_exporter.dump()

    for s1, s2 in zip(snapshop_1, snapshop_2, strict=False):
        assert snapshop_1[s1].sort(key=dict_sorter) == snapshop_2[s2].sort(key=dict_sorter)


@pytest.mark.parametrize(
    "backup_path",
    [
        test_data.backup_version_44e8d670719d_1,
        test_data.backup_version_44e8d670719d_2,
        test_data.backup_version_44e8d670719d_3,
        test_data.backup_version_44e8d670719d_4,
        test_data.backup_version_ba1e4a6cfe99_1,
        test_data.backup_version_bcfdad6b7355_1,
        test_data.backup_version_09aba125b57a_1,
        test_data.backup_version_86054b40fd06_1,
    ],
    ids=[
        "44e8d670719d_1: add extras to shopping lists, list items, and ingredient foods",
        "44e8d670719d_2: add extras to shopping lists, list items, and ingredient foods",
        "44e8d670719d_3: add extras to shopping lists, list items, and ingredient foods",
        "44e8d670719d_4: add extras to shopping lists, list items, and ingredient foods",
        "bcfdad6b7355_1: remove tool name and slug unique contraints",
        "ba1e4a6cfe99_1: added plural names and alias tables for foods and units",
        "09aba125b57a_1: add OIDC auth method (Safari-mangled ZIP structure)",
        "86054b40fd06_1: added query_filter_string to cookbook and mealplan",
    ],
)
def test_database_restore_data(backup_path: Path):
    """
    This tests real user backups to make sure the data is restored correctly. The data has been anonymized, but
    relationships and data types should be preserved.

    This test should verify all migrations that do some sort of database manipulation (e.g. populating a new column).
    If a new migration is added that does any sort of data manipulation, this test should be updated.
    """

    settings = get_app_settings()
    backup_v2 = BackupV2(settings.DB_URL)

    # create a backup of the existing data so we can restore it later
    original_data_backup = backup_v2.backup()

    try:
        assert backup_path.exists()
        backup_v2.restore(backup_path)

        # make sure migrations populated data successfully
        with session_context() as session:
            session = cast(Session, session)

            groups = session.query(Group).all()
            recipes = session.query(RecipeModel).all()
            shopping_lists = session.query(ShoppingList).all()
            labels = session.query(MultiPurposeLabel).all()

            foods = session.query(IngredientFoodModel).all()
            units = session.query(IngredientUnitModel).all()

            cookbooks = session.query(CookBook).all()
            mealplan_rules = session.query(GroupMealPlanRules).all()

            # 2023-02-14-20.45.41_5ab195a474eb_add_normalized_search_properties
            for recipe in recipes:
                if recipe.name:
                    assert recipe.name_normalized
                if recipe.description:
                    assert recipe.description_normalized

                for ingredient in recipe.recipe_ingredient:
                    if ingredient.note:
                        assert ingredient.note_normalized
                    if ingredient.original_text:
                        assert ingredient.original_text_normalized

            # 2023-02-21-22.03.19_b04a08da2108_added_shopping_list_label_settings
            for shopping_list in shopping_lists:
                group_labels = [label for label in labels if label.group_id == shopping_list.group_id]
                assert len(shopping_list.label_settings) == len(group_labels)
                for label_setting, label in zip(
                    sorted(shopping_list.label_settings, key=lambda x: x.label.id),
                    sorted(group_labels, key=lambda x: x.id),
                    strict=True,
                ):
                    assert label_setting.label == label

            # 2023-08-06-21.00.34_04ac51cbe9a4_added_group_slug
            for group in groups:
                assert group.slug

            # 2023-09-01-14.55.42_0341b154f79a_added_normalized_unit_and_food_names
            for food in foods:
                if food.name:
                    assert food.name_normalized

            for unit in units:
                assert unit.name_normalized
                if unit.abbreviation:
                    assert unit.abbreviation_normalized

            # 2024-03-18-02.28.15_d7c6efd2de42_migrate_favorites_and_ratings_to_user_ratings
            users_by_group_id: dict[GUID, list[User]] = {}
            for recipe in recipes:
                users = users_by_group_id.get(recipe.group_id)
                if users is None:
                    users = session.query(User).filter(User.group_id == recipe.group_id).all()
                    users_by_group_id[recipe.group_id] = users

                user_to_recipes = session.query(UserToRecipe).filter(UserToRecipe.recipe_id == recipe.id).all()
                user_ratings = [x.rating for x in user_to_recipes if x.rating]
                assert recipe.rating == (statistics.mean(user_ratings) if user_ratings else None)

            # 2024-10-08-21.17.31_86054b40fd06_added_query_filter_string_to_cookbook_and_mealplan
            for cookbook in cookbooks:
                parts = []
                if cookbook.categories:
                    relop = "CONTAINS ALL" if cookbook.require_all_categories else "IN"
                    vals = ",".join([f'"{cat.id}"' for cat in cookbook.categories])
                    parts.append(f"recipe_category.id {relop} [{vals}]")
                if cookbook.tags:
                    relop = "CONTAINS ALL" if cookbook.require_all_tags else "IN"
                    vals = ",".join([f'"{tag.id}"' for tag in cookbook.tags])
                    parts.append(f"tags.id {relop} [{vals}]")
                if cookbook.tools:
                    relop = "CONTAINS ALL" if cookbook.require_all_tools else "IN"
                    vals = ",".join([f'"{tool.id}"' for tool in cookbook.tools])
                    parts.append(f"tools.id {relop} [{vals}]")

                expected_query_filter_string = " AND ".join(parts)
                assert cookbook.query_filter_string == expected_query_filter_string

            for rule in mealplan_rules:
                parts = []
                if rule.categories:
                    vals = ",".join([f'"{cat.id}"' for cat in rule.categories])
                    parts.append(f"recipe_category.id CONTAINS ALL [{vals}]")
                if rule.tags:
                    vals = ",".join([f'"{tag.id}"' for tag in rule.tags])
                    parts.append(f"tags.id CONTAINS ALL [{vals}]")
                if rule.households:
                    vals = ",".join([f'"{household.id}"' for household in rule.households])
                    parts.append(f"household_id IN [{vals}]")

                expected_query_filter_string = " AND ".join(parts)
                assert rule.query_filter_string == expected_query_filter_string

    finally:
        backup_v2.restore(original_data_backup)
