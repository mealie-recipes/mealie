from fastapi import Depends, HTTPException

from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.household.household import HouseholdSummary
from mealie.schema.response.pagination import PaginationBase, PaginationQuery

router = UserAPIRouter(prefix="/groups/households", tags=["Groups: Households"])


@controller(router)
class GroupHouseholdsController(BaseUserController):
    @router.get("", response_model=PaginationBase[HouseholdSummary])
    def get_all_households(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repos.households.page_all(pagination=q, override=HouseholdSummary)

        response.set_pagination_guides(router.url_path_for("get_all_households"), q.model_dump())
        return response

    @router.get("/{household_slug}", response_model=HouseholdSummary)
    def get_one_household(self, household_slug: str):
        household = self.repos.households.get_by_slug_or_id(household_slug)

        if not household:
            raise HTTPException(status_code=404, detail="Household not found")
        return household.cast(HouseholdSummary)
