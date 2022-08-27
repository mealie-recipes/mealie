from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.core.exceptions import mealie_registered_exceptions
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

router = APIRouter(prefix="/groups/cookbooks", tags=["Groups: Cookbooks"], route_class=MealieCrudRoute)


@controller(router)
class GroupCookbookController(BaseCrudController):
    @cached_property
    def repo(self):
        return self.repos.cookbooks.by_group(self.group_id)

    def registered_exceptions(self, ex: type[Exception]) -> str:
        registered = {
            **mealie_registered_exceptions(self.translator),
        }
        return registered.get(ex, "An unexpected error occurred.")

    @cached_property
    def mixins(self):
        return HttpRepo[CreateCookBook, ReadCookBook, UpdateCookBook](
            self.repo,
            self.logger,
            self.registered_exceptions,
        )

    @router.get("", response_model=CookBookPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repo.page_all(
            pagination=q,
            override=ReadCookBook,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.dict())
        return response

    @router.post("", response_model=ReadCookBook, status_code=201)
    def create_one(self, data: CreateCookBook):
        data = mapper.cast(data, SaveCookBook, group_id=self.group_id)
        cookbook = self.mixins.create_one(data)

        if cookbook:
            self.publish_event(
                event_type=EventTypes.cookbook_created,
                document_data=EventCookbookData(operation=EventOperation.create, cookbook_id=cookbook.id),
                message=self.t("notifications.generic-created", name=cookbook.name),
            )

        return cookbook

    @router.put("", response_model=list[ReadCookBook])
    def update_many(self, data: list[UpdateCookBook]):
        updated = []

        for cookbook in data:
            cb = self.mixins.update_one(cookbook, cookbook.id)
            updated.append(cb)

        if updated:
            self.publish_event(
                event_type=EventTypes.cookbook_updated,
                document_data=EventCookbookBulkData(
                    operation=EventOperation.update, cookbook_ids=[cb.id for cb in updated]
                ),
            )

        return updated

    @router.get("/{item_id}", response_model=RecipeCookBook)
    def get_one(self, item_id: UUID4 | str):
        match_attr = "slug" if isinstance(item_id, str) else "id"
        cookbook = self.repo.get_one(item_id, match_attr)

        if cookbook is None:
            raise HTTPException(status_code=404)

        return cookbook.cast(
            RecipeCookBook,
            recipes=self.repos.recipes.by_group(self.group_id).by_category_and_tags(
                cookbook.categories,
                cookbook.tags,
                cookbook.tools,
                cookbook.require_all_categories,
                cookbook.require_all_tags,
                cookbook.require_all_tools,
            ),
        )

    @router.put("/{item_id}", response_model=ReadCookBook)
    def update_one(self, item_id: str, data: CreateCookBook):
        cookbook = self.mixins.update_one(data, item_id)  # type: ignore
        if cookbook:
            self.publish_event(
                event_type=EventTypes.cookbook_updated,
                document_data=EventCookbookData(operation=EventOperation.update, cookbook_id=cookbook.id),
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
                message=self.t("notifications.generic-deleted", name=cookbook.name),
            )

        return cookbook
