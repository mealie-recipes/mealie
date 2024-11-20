from uuid import UUID

from pydantic import UUID4

from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.household import HouseholdCreate, HouseholdRecipeSummary
from mealie.schema.household.household import HouseholdRecipeCreate, HouseholdRecipeUpdate
from mealie.schema.household.household_preferences import CreateHouseholdPreferences, SaveHouseholdPreferences
from mealie.schema.household.household_statistics import HouseholdStatistics
from mealie.services._base_service import BaseService


class HouseholdService(BaseService):
    def __init__(self, group_id: UUID4, household_id: UUID4, repos: AllRepositories):
        self.group_id = group_id
        self.household_id = household_id
        self.repos = repos
        super().__init__()

    def _get_recipe_id_from_slug(self, recipe_slug: str | UUID) -> UUID4 | None:
        if isinstance(recipe_slug, UUID):
            return recipe_slug

        try:
            return UUID(recipe_slug)
        except ValueError:
            pass

        recipe = self.repos.recipes.get_by_slug(self.group_id, recipe_slug)
        return recipe.id if recipe else None

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

    def get_household_recipe(self, recipe_slug: str) -> HouseholdRecipeSummary | None:
        """Returns recipe data for the current household"""
        recipe_id = self._get_recipe_id_from_slug(recipe_slug)
        household_recipe_out = self.repos.household_recipes.get_by_recipe(recipe_id) if recipe_id else None
        if household_recipe_out:
            return household_recipe_out.cast(HouseholdRecipeSummary)
        else:
            return HouseholdRecipeSummary(recipe_id=recipe_id)

    def set_household_recipe(self, recipe_slug: str | UUID, data: HouseholdRecipeUpdate) -> HouseholdRecipeSummary:
        """Sets the household's recipe data"""
        recipe_id = self._get_recipe_id_from_slug(recipe_slug)
        if not recipe_id:
            raise ValueError("Recipe not found")

        existing_household_recipe = self.repos.household_recipes.get_by_recipe(recipe_id)

        if existing_household_recipe:
            updated_data = existing_household_recipe.cast(HouseholdRecipeUpdate, **data.model_dump())
            household_recipe_out = self.repos.household_recipes.patch(existing_household_recipe.id, updated_data)
        else:
            create_data = HouseholdRecipeCreate(
                household_id=self.household_id, recipe_id=recipe_id, **data.model_dump()
            )
            household_recipe_out = self.repos.household_recipes.create(create_data)

        return household_recipe_out.cast(HouseholdRecipeSummary)
