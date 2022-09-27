from functools import cached_property

from fastapi import Depends, HTTPException
from pydantic import UUID4

from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.routers import MealieCrudRoute, UserAPIRouter
from mealie.schema.recipe.recipe_timeline_events import (
    RecipeTimelineEventCreate,
    RecipeTimelineEventIn,
    RecipeTimelineEventOut,
    RecipeTimelineEventPagination,
    RecipeTimelineEventUpdate,
)
from mealie.schema.response.pagination import PaginationQuery

events_router = UserAPIRouter(route_class=MealieCrudRoute, prefix="/{slug}/timeline/events")


@controller(events_router)
class RecipeTimelineEventsController(BaseUserController):
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

    def get_recipe_id_from_slug(self, slug: str) -> UUID4:
        recipe = self.repos.recipes.by_group(self.group_id).get_one(slug)
        if not recipe or self.group_id != recipe.group_id:
            raise HTTPException(status_code=404, detail="recipe not found")

        return recipe.id

    @events_router.get("", response_model=RecipeTimelineEventPagination)
    def get_all(self, slug: str, q: PaginationQuery = Depends(PaginationQuery)):
        recipe_id = self.get_recipe_id_from_slug(slug)
        recipe_filter = f"recipe_id = {recipe_id}"

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

        event = data.cast(RecipeTimelineEventCreate, recipe_id=self.get_recipe_id_from_slug(slug))
        return self.mixins.create_one(event)

    @events_router.get("/{item_id}", response_model=RecipeTimelineEventOut)
    def get_one(self, slug: str, item_id: UUID4):
        recipe_id = self.get_recipe_id_from_slug(slug)
        event = self.mixins.get_one(item_id)

        # validate that this event belongs to the given recipe slug
        if event.recipe_id != recipe_id:
            raise HTTPException(status_code=404, detail="recipe event not found")

        return event

    @events_router.put("/{item_id}", response_model=RecipeTimelineEventOut)
    def update_one(self, slug: str, item_id: UUID4, data: RecipeTimelineEventUpdate):
        # validate that this event belongs to the given recipe slug
        self.get_one(slug=slug, item_id=item_id)

        return self.mixins.update_one(data, item_id)

    @events_router.delete("/{item_id}", response_model=RecipeTimelineEventOut)
    def delete_one(self, slug: str, item_id: UUID4):
        # validate that this event belongs to the given recipe slug
        self.get_one(slug=slug, item_id=item_id)

        return self.mixins.delete_one(item_id)
