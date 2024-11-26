from functools import cached_property

from fastapi import Depends, HTTPException, status

from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.household import HouseholdInDB, HouseholdRecipeSummary
from mealie.schema.household.household_permissions import SetPermissions
from mealie.schema.household.household_preferences import ReadHouseholdPreferences, UpdateHouseholdPreferences
from mealie.schema.household.household_statistics import HouseholdStatistics
from mealie.schema.response.pagination import PaginationBase, PaginationQuery
from mealie.schema.user.user import UserOut
from mealie.services.household_services.household_service import HouseholdService

router = UserAPIRouter(prefix="/households", tags=["Households: Self Service"])


@controller(router)
class HouseholdSelfServiceController(BaseUserController):
    @cached_property
    def service(self) -> HouseholdService:
        return HouseholdService(self.group_id, self.household_id, self.repos)

    @router.get("/self", response_model=HouseholdInDB)
    def get_logged_in_user_household(self):
        """Returns the Household Data for the Current User"""
        return self.household

    @router.get("/self/recipes/{recipe_slug}", response_model=HouseholdRecipeSummary)
    def get_household_recipe(self, recipe_slug: str):
        """Returns recipe data for the current household"""
        response = self.service.get_household_recipe(recipe_slug)
        if not response:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Recipe not found")

        return response

    @router.get("/members", response_model=PaginationBase[UserOut])
    def get_household_members(self, q: PaginationQuery = Depends()):
        """Returns all users belonging to the current household"""

        qf_part = f"household_id={self.household_id}"
        if q.query_filter:
            q.query_filter = f"({q.query_filter}) AND {qf_part}"
        else:
            q.query_filter = qf_part

        response = self.repos.users.page_all(q, override=UserOut)

        response.set_pagination_guides(router.url_path_for("get_household_members"), q.model_dump())
        return response

    @router.get("/preferences", response_model=ReadHouseholdPreferences)
    def get_household_preferences(self):
        return self.household.preferences

    @router.put("/preferences", response_model=ReadHouseholdPreferences)
    def update_household_preferences(self, new_pref: UpdateHouseholdPreferences):
        self.checks.can_manage_household()

        return self.repos.household_preferences.update(self.household_id, new_pref)

    @router.put("/permissions", response_model=UserOut)
    def set_member_permissions(self, permissions: SetPermissions):
        self.checks.can_manage()

        target_user = self.repos.users.get_one(permissions.user_id)

        if not target_user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

        if target_user.group_id != self.group_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User is not a member of this group")

        if target_user.household_id != self.household_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User is not a member of this household")

        target_user.can_invite = permissions.can_invite
        target_user.can_manage = permissions.can_manage
        target_user.can_manage_household = permissions.can_manage_household
        target_user.can_organize = permissions.can_organize

        return self.repos.users.update(permissions.user_id, target_user)

    @router.get("/statistics", response_model=HouseholdStatistics)
    def get_statistics(self):
        return self.service.calculate_statistics()
