from collections import defaultdict
from functools import cached_property
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.core.exceptions import mealie_registered_exceptions
from mealie.repos.all_repositories import get_repositories
from mealie.routes._base import BaseCrudController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.routers import MealieCrudRoute
from mealie.schema import mapper
from mealie.schema.cookbook import CreateCookBook, ReadCookBook, RecipeCookBook, SaveCookBook, UpdateCookBook
from mealie.schema.cookbook.cookbook import CookBookPagination
from mealie.schema.response.pagination import PaginationQuery
from mealie.services.event_bus_service.event_types import (
    EventCookbookBulkData,
    EventCookbookData,
    EventOperation,
    EventTypes,
)

router = APIRouter(prefix="/households/cookbooks", tags=["Households: Cookbooks"], route_class=MealieCrudRoute)


@controller(router)
class GroupCookbookController(BaseCrudController):
    @cached_property
    def cookbooks(self):
        return self.repos.cookbooks

    @cached_property
    def group_cookbooks(self):
        return get_repositories(self.session, group_id=self.group_id, household_id=None).cookbooks

    def registered_exceptions(self, ex: type[Exception]) -> str:
        registered = {
            **mealie_registered_exceptions(self.translator),
        }
        return registered.get(ex, self.t("generic.server-error"))

    @cached_property
    def mixins(self):
        return HttpRepo[CreateCookBook, ReadCookBook, UpdateCookBook](
            self.cookbooks,
            self.logger,
            self.registered_exceptions,
        )

    @router.get("", response_model=CookBookPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        # Fetch all cookbooks for the group, rather than the household
        response = self.group_cookbooks.page_all(
            pagination=q,
            override=ReadCookBook,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=ReadCookBook, status_code=201)
    def create_one(self, data: CreateCookBook):
        data = mapper.cast(data, SaveCookBook, group_id=self.group_id, household_id=self.household_id)
        cookbook = self.mixins.create_one(data)

        if cookbook:
            self.publish_event(
                event_type=EventTypes.cookbook_created,
                document_data=EventCookbookData(operation=EventOperation.create, cookbook_id=cookbook.id),
                group_id=cookbook.group_id,
                household_id=cookbook.household_id,
                message=self.t("notifications.generic-created", name=cookbook.name),
            )

        return cookbook

    @router.put("", response_model=list[ReadCookBook])
    def update_many(self, data: list[UpdateCookBook]):
        updated_by_group_and_household: defaultdict[UUID4, defaultdict[UUID4, list[ReadCookBook]]] = defaultdict(
            lambda: defaultdict(list)
        )

        for cookbook in data:
            cb = self.mixins.update_one(cookbook, cookbook.id)
            updated_by_group_and_household[cb.group_id][cb.household_id].append(cb)

        all_updated: list[ReadCookBook] = []
        if updated_by_group_and_household:
            for group_id, household_dict in updated_by_group_and_household.items():
                for household_id, updated_cookbooks in household_dict.items():
                    all_updated.extend(updated_cookbooks)
                    self.publish_event(
                        event_type=EventTypes.cookbook_updated,
                        document_data=EventCookbookBulkData(
                            operation=EventOperation.update, cookbook_ids=[cb.id for cb in updated_cookbooks]
                        ),
                        group_id=group_id,
                        household_id=household_id,
                    )

        return all_updated

    @router.get("/{item_id}", response_model=RecipeCookBook)
    def get_one(self, item_id: UUID4 | str):
        if isinstance(item_id, UUID):
            match_attr = "id"
        else:
            try:
                UUID(item_id)
                match_attr = "id"
            except ValueError:
                match_attr = "slug"

        # Allow fetching other households' cookbooks
        cookbook = self.group_cookbooks.get_one(item_id, match_attr)

        if cookbook is None:
            raise HTTPException(status_code=404)

        recipe_pagination = self.repos.recipes.page_all(PaginationQuery(page=1, per_page=-1, cookbook=cookbook))
        return cookbook.cast(RecipeCookBook, recipes=recipe_pagination.items)

    @router.put("/{item_id}", response_model=ReadCookBook)
    def update_one(self, item_id: str, data: CreateCookBook):
        cookbook = self.mixins.update_one(data, item_id)  # type: ignore
        if cookbook:
            self.publish_event(
                event_type=EventTypes.cookbook_updated,
                document_data=EventCookbookData(operation=EventOperation.update, cookbook_id=cookbook.id),
                group_id=cookbook.group_id,
                household_id=cookbook.household_id,
                message=self.t("notifications.generic-updated", name=cookbook.name),
            )

        return cookbook

    @router.delete("/{item_id}", response_model=ReadCookBook)
    def delete_one(self, item_id: str):
        cookbook = self.mixins.delete_one(item_id)
        if cookbook:
            self.publish_event(
                event_type=EventTypes.cookbook_deleted,
                document_data=EventCookbookData(operation=EventOperation.delete, cookbook_id=cookbook.id),
                group_id=cookbook.group_id,
                household_id=cookbook.household_id,
                message=self.t("notifications.generic-deleted", name=cookbook.name),
            )

        return cookbook
