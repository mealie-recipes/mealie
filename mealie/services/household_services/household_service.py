from pydantic import UUID4

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.household.household import HouseholdBase
from mealie.schema.household.household_preferences import CreateHouseholdPreferences
from mealie.services._base_service import BaseService


class HouseholdService(BaseService):
    def __init__(self, group_id: UUID4, household_id: UUID4, repos: AllRepositories):
        self.group_id = group_id
        self.household_id = household_id
        self.repos = repos
        super().__init__()

    @staticmethod
    def create_household(
        repos: AllRepositories, h_base: HouseholdBase, prefs: CreateHouseholdPreferences | None = None
    ):
        new_household = repos.households.create(h_base)
        if prefs is None:
            prefs = CreateHouseholdPreferences(group_id=new_household.group_id, household_id=new_household.id)
        else:
            prefs.group_id = new_household.group_id
            prefs.household_id = new_household.id

        repos.household_preferences.create(prefs)
        return new_household
