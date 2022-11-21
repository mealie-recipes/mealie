from functools import cached_property

from fastapi import Depends, HTTPException
from pydantic import UUID4

from mealie.routes._base import BaseCrudController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.routers import MealieCrudRoute, UserAPIRouter
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_timeline_events import (
    RecipeTimelineEventCreate,
    RecipeTimelineEventIn,
    RecipeTimelineEventOut,
    RecipeTimelineEventPagination,
    RecipeTimelineEventUpdate,
)
from mealie.schema.response.pagination import PaginationQuery
from mealie.services import urls
from mealie.services.event_bus_service.event_types import EventOperation, EventRecipeTimelineEventData, EventTypes

events_router = UserAPIRouter(route_class=MealieCrudRoute, prefix="/{slug}/timeline/events")


@controller(events_router)
class RecipeTimelineEventsController(BaseCrudController):
    @cached_property
    def repo(self):
        return self.repos.recipe_timeline_events

    @cached_property
    def mixins(self):
        return HttpRepo[RecipeTimelineEventCreate, RecipeTimelineEventOut, RecipeTimelineEventUpdate](
            self.repo,
            self.logger,
            self.registered_exceptions,
        )

    def get_recipe_from_slug(self, slug: str) -> Recipe:
        recipe = self.repos.recipes.by_group(self.group_id).get_one(slug)
        if not recipe or self.group_id != recipe.group_id:
            raise HTTPException(status_code=404, detail="recipe not found")

        return recipe

    @events_router.get("", response_model=RecipeTimelineEventPagination)
    def get_all(self, slug: str, q: PaginationQuery = Depends(PaginationQuery)):
        recipe = self.get_recipe_from_slug(slug)
        recipe_filter = f"recipe_id = {recipe.id}"

        if q.query_filter:
            q.query_filter = f"({q.query_filter}) AND {recipe_filter}"

        else:
            q.query_filter = recipe_filter

        response = self.repo.page_all(
            pagination=q,
            override=RecipeTimelineEventOut,
        )

        response.set_pagination_guides(events_router.url_path_for("get_all", slug=slug), q.dict())
        return response

    @events_router.post("", response_model=RecipeTimelineEventOut, status_code=201)
    def create_one(self, slug: str, data: RecipeTimelineEventIn):
        # if the user id is not specified, use the currently-authenticated user
        data.user_id = data.user_id or self.user.id

        recipe = self.get_recipe_from_slug(slug)
        event_data = data.cast(RecipeTimelineEventCreate, recipe_id=recipe.id)
        event = self.mixins.create_one(event_data)

        self.publish_event(
            event_type=EventTypes.recipe_updated,
            document_data=EventRecipeTimelineEventData(
                operation=EventOperation.create, recipe_slug=recipe.slug, recipe_timeline_event_id=event.id
            ),
            message=self.t(
                "notifications.generic-updated-with-url",
                name=recipe.name,
                url=urls.recipe_url(slug, self.settings.BASE_URL),
            ),
        )

        return event

    @events_router.get("/{item_id}", response_model=RecipeTimelineEventOut)
    def get_one(self, slug: str, item_id: UUID4):
        recipe = self.get_recipe_from_slug(slug)
        event = self.mixins.get_one(item_id)

        # validate that this event belongs to the given recipe slug
        if event.recipe_id != recipe.id:
            raise HTTPException(status_code=404, detail="recipe event not found")

        return event

    @events_router.put("/{item_id}", response_model=RecipeTimelineEventOut)
    def update_one(self, slug: str, item_id: UUID4, data: RecipeTimelineEventUpdate):
        recipe = self.get_recipe_from_slug(slug)
        event = self.mixins.get_one(item_id)

        # validate that this event belongs to the given recipe slug
        if event.recipe_id != recipe.id:
            raise HTTPException(status_code=404, detail="recipe event not found")

        event = self.mixins.update_one(data, item_id)

        self.publish_event(
            event_type=EventTypes.recipe_updated,
            document_data=EventRecipeTimelineEventData(
                operation=EventOperation.update, recipe_slug=recipe.slug, recipe_timeline_event_id=event.id
            ),
            message=self.t(
                "notifications.generic-updated-with-url",
                name=recipe.name,
                url=urls.recipe_url(slug, self.settings.BASE_URL),
            ),
        )

        return event

    @events_router.delete("/{item_id}", response_model=RecipeTimelineEventOut)
    def delete_one(self, slug: str, item_id: UUID4):
        recipe = self.get_recipe_from_slug(slug)
        event = self.mixins.get_one(item_id)

        # validate that this event belongs to the given recipe slug
        if event.recipe_id != recipe.id:
            raise HTTPException(status_code=404, detail="recipe event not found")

        event = self.mixins.delete_one(item_id)

        self.publish_event(
            event_type=EventTypes.recipe_updated,
            document_data=EventRecipeTimelineEventData(
                operation=EventOperation.delete, recipe_slug=recipe.slug, recipe_timeline_event_id=event.id
            ),
            message=self.t(
                "notifications.generic-updated-with-url",
                name=recipe.name,
                url=urls.recipe_url(slug, self.settings.BASE_URL),
            ),
        )

        return event
