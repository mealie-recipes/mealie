from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import UUID4

from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema import mapper
from mealie.schema.recipe import RecipeTagResponse, TagIn
from mealie.schema.recipe.recipe import RecipeTag, RecipeTagPagination
from mealie.schema.recipe.recipe_category import TagSave
from mealie.schema.response.pagination import PaginationQuery
from mealie.services import urls
from mealie.services.event_bus_service.event_bus_service import EventBusService, EventSource, EventTrigger
from mealie.services.event_bus_service.message_types import EventTypes

router = APIRouter(prefix="/tags", tags=["Organizer: Tags"])


@controller(router)
class TagController(BaseUserController):

    event_bus: EventBusService = Depends(EventBusService)

    @cached_property
    def repo(self):
        return self.repos.tags.by_group(self.group_id)

    @cached_property
    def mixins(self):
        return HttpRepo(self.repo, self.deps.logger)

    @router.get("", response_model=RecipeTagPagination)
    async def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        """Returns a list of available tags in the database"""
        response = self.repo.page_all(
            pagination=q,
            override=RecipeTag,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.dict())
        return response

    @router.get("/empty")
    def get_empty_tags(self):
        """Returns a list of tags that do not contain any recipes"""
        return self.repo.get_empty()

    @router.get("/{item_id}", response_model=RecipeTagResponse)
    def get_one(self, item_id: UUID4):
        """Returns a list of recipes associated with the provided tag."""
        return self.mixins.get_one(item_id)

    @router.post("", status_code=201)
    def create_one(
        self,
        tag: TagIn,
        event_trigger: EventTrigger = Query(EventTrigger.generic, description="The service triggering this event"),
        event_trigger_id: str
        | None = Query(None, description="Unique identifier for the service triggering this event"),
    ):
        """Creates a Tag in the database"""
        save_data = mapper.cast(tag, TagSave, group_id=self.group_id)
        data = self.repo.create(save_data)
        if data:
            self.event_bus.dispatch(
                self.deps.acting_user.group_id,
                EventTypes.tag_created,
                msg=self.t(
                    "notifications.generic-created-with-url",
                    name=data.name,
                    url=urls.tag_url(data.slug, self.deps.settings.BASE_URL),
                ),
                event_source=EventSource(
                    actor=self.user.id,
                    event_trigger=event_trigger,
                    event_trigger_id=event_trigger_id,
                    event_type="create",
                    item_type="tag",
                    item_id=data.id,
                    slug=data.slug,
                ),
            )
        return data

    @router.put("/{item_id}", response_model=RecipeTagResponse)
    def update_one(
        self,
        item_id: UUID4,
        new_tag: TagIn,
        event_trigger: EventTrigger = Query(EventTrigger.generic, description="The service triggering this event"),
        event_trigger_id: str
        | None = Query(None, description="Unique identifier for the service triggering this event"),
    ):
        """Updates an existing Tag in the database"""
        save_data = mapper.cast(new_tag, TagSave, group_id=self.group_id)
        data = self.repo.update(item_id, save_data)
        if data:
            self.event_bus.dispatch(
                self.deps.acting_user.group_id,
                EventTypes.tag_updated,
                msg=self.t(
                    "notifications.generic-updated-with-url",
                    name=data.name,
                    url=urls.tag_url(data.slug, self.deps.settings.BASE_URL),
                ),
                event_source=EventSource(
                    actor=self.user.id,
                    event_trigger=event_trigger,
                    event_trigger_id=event_trigger_id,
                    event_type="update",
                    item_type="tag",
                    item_id=data.id,
                    slug=data.slug,
                ),
            )
        return data

    @router.delete("/{item_id}")
    def delete_recipe_tag(
        self,
        item_id: UUID4,
        event_trigger: EventTrigger = Query(EventTrigger.generic, description="The service triggering this event"),
        event_trigger_id: str
        | None = Query(None, description="Unique identifier for the service triggering this event"),
    ):
        """Removes a recipe tag from the database. Deleting a
        tag does not impact a recipe. The tag will be removed
        from any recipes that contain it"""

        try:
            data = self.repo.delete(item_id)
        except Exception as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST) from e

        if data:
            self.event_bus.dispatch(
                self.deps.acting_user.group_id,
                EventTypes.tag_deleted,
                msg=self.t("notifications.generic-deleted", name=data.name),
                event_source=EventSource(
                    actor=self.user.id,
                    event_trigger=event_trigger,
                    event_trigger_id=event_trigger_id,
                    event_type="delete",
                    item_type="tag",
                    item_id=data.id,
                    slug=data.slug,
                ),
            )

    @router.get("/slug/{tag_slug}", response_model=RecipeTagResponse)
    async def get_one_by_slug(self, tag_slug: str):
        return self.repo.get_one(tag_slug, "slug", override_schema=RecipeTagResponse)
