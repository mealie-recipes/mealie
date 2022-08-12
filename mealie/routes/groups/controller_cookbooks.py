from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.core.exceptions import mealie_registered_exceptions
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.routers import MealieCrudRoute
from mealie.schema import mapper
from mealie.schema.cookbook import CreateCookBook, ReadCookBook, RecipeCookBook, SaveCookBook, UpdateCookBook
from mealie.schema.cookbook.cookbook import CookBookPagination
from mealie.schema.response.pagination import PaginationQuery
from mealie.services.event_bus_service.event_bus_service import EventBusService, EventSource
from mealie.services.event_bus_service.message_types import EventTypes

router = APIRouter(prefix="/groups/cookbooks", tags=["Groups: Cookbooks"], route_class=MealieCrudRoute)


@controller(router)
class GroupCookbookController(BaseUserController):

    event_bus: EventBusService = Depends(EventBusService)

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
        val = self.mixins.create_one(data)

        if val:
            self.event_bus.dispatch(
                self.user.group_id,
                EventTypes.cookbook_created,
                msg=self.t("notifications.generic-created", name=val.name),
                event_source=EventSource(event_type="create", item_type="cookbook", item_id=val.id, slug=val.slug),
            )
        return val

    @router.put("", response_model=list[ReadCookBook])
    def update_many(self, data: list[UpdateCookBook]):
        updated = []

        for cookbook in data:
            cb = self.mixins.update_one(cookbook, cookbook.id)
            updated.append(cb)

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
        val = self.mixins.update_one(data, item_id)  # type: ignore
        if val:
            self.event_bus.dispatch(
                self.user.group_id,
                EventTypes.cookbook_updated,
                msg=self.t("notifications.generic-updated", name=val.name),
                event_source=EventSource(event_type="update", item_type="cookbook", item_id=val.id, slug=val.slug),
            )

        return val

    @router.delete("/{item_id}", response_model=ReadCookBook)
    def delete_one(self, item_id: str):
        val = self.mixins.delete_one(item_id)
        if val:
            self.event_bus.dispatch(
                self.user.group_id,
                EventTypes.cookbook_deleted,
                msg=self.t("notifications.generic-deleted", name=val.name),
                event_source=EventSource(event_type="delete", item_type="cookbook", item_id=val.id, slug=val.slug),
            )
        return val
