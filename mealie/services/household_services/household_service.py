from pydantic import UUID4

from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.household.household import HouseholdCreate
from mealie.schema.household.household_preferences import CreateHouseholdPreferences, SaveHouseholdPreferences
from mealie.schema.household.household_statistics import HouseholdStatistics
from mealie.services._base_service import BaseService


class HouseholdService(BaseService):
    def __init__(self, group_id: UUID4, household_id: UUID4, repos: AllRepositories):
        self.group_id = group_id
        self.household_id = household_id
        self.repos = repos
        super().__init__()

    @staticmethod
    def create_household(
        repos: AllRepositories, h_base: HouseholdCreate, prefs: CreateHouseholdPreferences | None = None
    ):
        new_household = repos.households.create(h_base)
        if prefs is None:
            group = repos.groups.get_one(new_household.group_id)
            if group and group.preferences:
                prefs = CreateHouseholdPreferences(
                    private_household=group.preferences.private_group,
                    recipe_public=not group.preferences.private_group,
                )
            else:
                prefs = CreateHouseholdPreferences()
        save_prefs = prefs.cast(SaveHouseholdPreferences, household_id=new_household.id)

        household_repos = get_repositories(
            repos.session, group_id=new_household.group_id, household_id=new_household.id
        )
        household_repos.household_preferences.create(save_prefs)
        return new_household

    def calculate_statistics(
        self, group_id: UUID4 | None = None, household_id: UUID4 | None = None
    ) -> HouseholdStatistics:
        """
        calculate_statistics calculates the statistics for the group and returns
        a HouseholdStatistics object.
        """
        group_id = group_id or self.group_id
        household_id = household_id or self.household_id

        return self.repos.households.statistics(group_id, household_id)
