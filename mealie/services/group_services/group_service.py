from pydantic import UUID4

from mealie.pkgs.stats import fs_stats
from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group.group_preferences import CreateGroupPreferences
from mealie.schema.group.group_statistics import GroupStorage
from mealie.schema.user.user import GroupBase
from mealie.services._base_service import BaseService

ALLOWED_SIZE = 500 * fs_stats.megabyte


class GroupService(BaseService):
    def __init__(self, group_id: UUID4, repos: AllRepositories):
        self.group_id = group_id
        self.repos = repos
        super().__init__()

    @staticmethod
    def create_group(repos: AllRepositories, g_base: GroupBase, prefs: CreateGroupPreferences | None = None):
        """
        Creates a new group in the database with the required associated table references to ensure
        the group includes required preferences.
        """
        new_group = repos.groups.create(g_base)

        if prefs is None:
            prefs = CreateGroupPreferences(group_id=new_group.id)
        else:
            prefs.group_id = new_group.id

        repos.group_preferences.create(prefs)

        return new_group

    def calculate_group_storage(self, group_id: None | UUID4 = None) -> GroupStorage:
        """
        calculate_group_storage calculates the storage used by the group and returns
        a GroupStorage object.
        """

        # we need all recipes from all households, not just our household
        group_repos = get_repositories(self.repos.session, group_id, None)

        target_id = group_id or self.group_id

        all_ids = group_repos.recipes.all_ids(target_id)

        used_size = sum(
            fs_stats.get_dir_size(f"{self.directories.RECIPE_DATA_DIR}/{str(recipe_id)}") for recipe_id in all_ids
        )

        return GroupStorage.bytes(used_size, ALLOWED_SIZE)
