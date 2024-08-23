from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy import func, select

from mealie.db.models.users.users import User
from mealie.schema.household.household import (
    HouseholdCreate,
    HouseholdInDB,
    HouseholdPagination,
    UpdateHouseholdAdmin,
)
from mealie.schema.mapper import mapper
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.response.responses import ErrorResponse
from mealie.services.household_services.household_service import HouseholdService

from .._base import BaseAdminController, controller
from .._base.mixins import HttpRepo

router = APIRouter(prefix="/households")


@controller(router)
class AdminHouseholdManagementRoutes(BaseAdminController):
    @cached_property
    def repo(self):
        if not self.user:
            raise Exception("No user is logged in.")

        return self.repos.households

    # =======================================================================
    # CRUD Operations

    @property
    def mixins(self):
        return HttpRepo[HouseholdCreate, HouseholdInDB, UpdateHouseholdAdmin](
            self.repo,
            self.logger,
            self.registered_exceptions,
        )

    @router.get("", response_model=HouseholdPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repo.page_all(
            pagination=q,
            override=HouseholdInDB,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=HouseholdInDB, status_code=status.HTTP_201_CREATED)
    def create_one(self, data: HouseholdCreate):
        return HouseholdService.create_household(self.repos, data)

    @router.get("/{item_id}", response_model=HouseholdInDB)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=HouseholdInDB)
    def update_one(self, item_id: UUID4, data: UpdateHouseholdAdmin):
        household = self.repo.get_one(item_id)

        if data.preferences:
            preferences = self.repos.household_preferences.get_one(value=item_id, key="household_id")
            preferences = mapper(data.preferences, preferences)
            household.preferences = self.repos.household_preferences.update(item_id, preferences)

        if data.name not in ["", household.name]:
            # only update the household if the name changed, since the name is the only field that can be updated
            household.name = data.name
            household = self.repo.update(item_id, household)

        return household

    @router.delete("/{item_id}", response_model=HouseholdInDB)
    def delete_one(self, item_id: UUID4):
        item = self.repo.get_one(item_id)
        if item:
            stmt = select(func.count(User.id)).filter_by(group_id=item.group_id, household_id=item_id)
            user_count = self.session.scalar(stmt)
            if user_count:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorResponse.respond(message="Cannot delete household with users"),
                )

        return self.mixins.delete_one(item_id)
