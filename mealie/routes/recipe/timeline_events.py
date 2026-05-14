import shutil
from functools import cached_property

from fastapi import Depends, File, Form, HTTPException
from pydantic import UUID4

from mealie.lang.providers import get_locale_provider
from mealie.repos.all_repositories import get_repositories
from mealie.routes._base import BaseCrudController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.routers import MealieCrudRoute, UserAPIRouter
from mealie.schema.recipe.recipe_timeline_events import (
    RecipeTimelineEventCreate,
    RecipeTimelineEventIn,
    RecipeTimelineEventOut,
    RecipeTimelineEventPagination,
    RecipeTimelineEventUpdate,
    TimelineEventImage,
    TimelineEventType,
)
from mealie.schema.recipe.request_helpers import UpdateImageResponse
from mealie.schema.response.pagination import PaginationQuery
from mealie.services import urls
from mealie.services.event_bus_service.event_types import EventOperation, EventRecipeTimelineEventData, EventTypes
from mealie.services.recipe.recipe_data_service import RecipeDataService

router = UserAPIRouter(route_class=MealieCrudRoute, prefix="/timeline/events")


@controller(router)
class RecipeTimelineEventsController(BaseCrudController):
    @cached_property
    def repo(self):
        return self.repos.recipe_timeline_events

    @cached_property
    def group_recipes(self):
        return get_repositories(self.session, group_id=self.group_id, household_id=None).recipes

    @cached_property
    def mixins(self):
        return HttpRepo[RecipeTimelineEventCreate, RecipeTimelineEventOut, RecipeTimelineEventUpdate](
            self.repo,
            self.logger,
            self.registered_exceptions,
        )

    def _translate_event_subject(self, event: RecipeTimelineEventOut) -> None:
        """Translate auto-generated event subjects stored as i18n key references.

        Subjects are stored as ``<i18n-key>|<name>`` (e.g. ``recipe.made-this-for-dinner|Alice``).
        Falls back to en-US when the requested locale has not yet been translated.
        """
        if event.event_type == TimelineEventType.info.value and "|" in event.subject:
            key, _, name = event.subject.partition("|")
            if key.startswith("recipe."):
                translated = self.t(key, name=name)
                if translated == key:
                    translated = get_locale_provider("en-US").t(key, name=name)
                if translated != key:
                    event.subject = translated

    @router.get("", response_model=RecipeTimelineEventPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repo.page_all(
            pagination=q,
            override=RecipeTimelineEventOut,
        )

        for event in response.items:
            self._translate_event_subject(event)

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=RecipeTimelineEventOut, status_code=201)
    def create_one(self, data: RecipeTimelineEventIn):
        # if the user id is not specified, use the currently-authenticated user
        data.user_id = data.user_id or self.user.id

        recipe = self.group_recipes.get_one(data.recipe_id, "id")
        if not recipe:
            raise HTTPException(status_code=404, detail="recipe not found")

        event_data = data.cast(RecipeTimelineEventCreate)
        event = self.mixins.create_one(event_data)

        self.publish_event(
            event_type=EventTypes.recipe_updated,
            document_data=EventRecipeTimelineEventData(
                operation=EventOperation.create, recipe_slug=recipe.slug, recipe_timeline_event_id=event.id
            ),
            group_id=recipe.group_id,
            household_id=recipe.household_id,
            message=self.t(
                "notifications.generic-updated-with-url",
                name=recipe.name,
                url=urls.recipe_url(self.group.slug, recipe.slug, self.settings.BASE_URL),
            ),
        )

        return event

    @router.get("/{item_id}", response_model=RecipeTimelineEventOut)
    def get_one(self, item_id: UUID4):
        event = self.mixins.get_one(item_id)
        self._translate_event_subject(event)
        return event

    @router.put("/{item_id}", response_model=RecipeTimelineEventOut)
    def update_one(self, item_id: UUID4, data: RecipeTimelineEventUpdate):
        event = self.mixins.patch_one(data, item_id)
        recipe = self.group_recipes.get_one(event.recipe_id, "id")
        if recipe:
            self.publish_event(
                event_type=EventTypes.recipe_updated,
                document_data=EventRecipeTimelineEventData(
                    operation=EventOperation.update, recipe_slug=recipe.slug, recipe_timeline_event_id=event.id
                ),
                group_id=recipe.group_id,
                household_id=recipe.household_id,
                message=self.t(
                    "notifications.generic-updated-with-url",
                    name=recipe.name,
                    url=urls.recipe_url(self.group.slug, recipe.slug, self.settings.BASE_URL),
                ),
            )

        return event

    @router.delete("/{item_id}", response_model=RecipeTimelineEventOut)
    def delete_one(self, item_id: UUID4):
        event = self.mixins.delete_one(item_id)
        if event.image_dir.exists():
            try:
                shutil.rmtree(event.image_dir)
            except FileNotFoundError:
                pass

        recipe = self.group_recipes.get_one(event.recipe_id, "id")
        if recipe:
            self.publish_event(
                event_type=EventTypes.recipe_updated,
                document_data=EventRecipeTimelineEventData(
                    operation=EventOperation.delete, recipe_slug=recipe.slug, recipe_timeline_event_id=event.id
                ),
                group_id=recipe.group_id,
                household_id=recipe.household_id,
                message=self.t(
                    "notifications.generic-updated-with-url",
                    name=recipe.name,
                    url=urls.recipe_url(self.group.slug, recipe.slug, self.settings.BASE_URL),
                ),
            )

        return event

    # ==================================================================================================================
    # Image and Assets

    @router.put("/{item_id}/image", response_model=UpdateImageResponse)
    def update_event_image(self, item_id: UUID4, image: bytes = File(...), extension: str = Form(...)):
        event = self.mixins.get_one(item_id)
        data_service = RecipeDataService(event.recipe_id)
        data_service.write_image(image, extension, event.image_dir)

        if event.image != TimelineEventImage.has_image.value:
            event.image = TimelineEventImage.has_image
            event = self.mixins.patch_one(event.cast(RecipeTimelineEventUpdate), event.id)
            recipe = self.group_recipes.get_one(event.recipe_id, "id")
            if recipe:
                self.publish_event(
                    event_type=EventTypes.recipe_updated,
                    document_data=EventRecipeTimelineEventData(
                        operation=EventOperation.update, recipe_slug=recipe.slug, recipe_timeline_event_id=event.id
                    ),
                    group_id=recipe.group_id,
                    household_id=recipe.household_id,
                    message=self.t(
                        "notifications.generic-updated-with-url",
                        name=recipe.name,
                        url=urls.recipe_url(self.group.slug, recipe.slug, self.settings.BASE_URL),
                    ),
                )

        return UpdateImageResponse(image=TimelineEventImage.has_image.value)
