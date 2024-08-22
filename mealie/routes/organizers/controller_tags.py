from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from mealie.routes._base import BaseCrudController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema import mapper
from mealie.schema.recipe import RecipeTagResponse, TagIn
from mealie.schema.recipe.recipe import RecipeTag, RecipeTagPagination
from mealie.schema.recipe.recipe_category import TagSave
from mealie.schema.response.pagination import PaginationQuery
from mealie.services import urls
from mealie.services.event_bus_service.event_types import EventOperation, EventTagData, EventTypes

router = APIRouter(prefix="/tags", tags=["Organizer: Tags"])


@controller(router)
class TagController(BaseCrudController):
    @cached_property
    def repo(self):
        return self.repos.tags

    @cached_property
    def mixins(self):
        return HttpRepo(self.repo, self.logger)

    @router.get("", response_model=RecipeTagPagination)
    async def get_all(self, q: PaginationQuery = Depends(PaginationQuery), search: str | None = None):
        """Returns a list of available tags in the database"""
        response = self.repo.page_all(
            pagination=q,
            override=RecipeTag,
            search=search,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
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
    def create_one(self, tag: TagIn):
        """Creates a Tag in the database"""
        save_data = mapper.cast(tag, TagSave, group_id=self.group_id)
        new_tag = self.repo.create(save_data)

        if new_tag:
            self.publish_event(
                event_type=EventTypes.tag_created,
                document_data=EventTagData(operation=EventOperation.create, tag_id=new_tag.id),
                group_id=new_tag.group_id,
                household_id=None,
                message=self.t(
                    "notifications.generic-created-with-url",
                    name=new_tag.name,
                    url=urls.tag_url(new_tag.slug, self.settings.BASE_URL),
                ),
            )

        return new_tag

    @router.put("/{item_id}", response_model=RecipeTagResponse)
    def update_one(self, item_id: UUID4, new_tag: TagIn):
        """Updates an existing Tag in the database"""
        save_data = mapper.cast(new_tag, TagSave, group_id=self.group_id)
        tag = self.repo.update(item_id, save_data)

        if tag:
            self.publish_event(
                event_type=EventTypes.tag_updated,
                document_data=EventTagData(operation=EventOperation.update, tag_id=tag.id),
                group_id=tag.group_id,
                household_id=None,
                message=self.t(
                    "notifications.generic-updated-with-url",
                    name=tag.name,
                    url=urls.tag_url(tag.slug, self.settings.BASE_URL),
                ),
            )

        return tag

    @router.delete("/{item_id}")
    def delete_recipe_tag(self, item_id: UUID4):
        """
        Removes a recipe tag from the database. Deleting a
        tag does not impact a recipe. The tag will be removed
        from any recipes that contain it
        """

        try:
            tag = self.repo.delete(item_id)
        except Exception as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST) from e

        if tag:
            self.publish_event(
                event_type=EventTypes.tag_deleted,
                document_data=EventTagData(operation=EventOperation.delete, tag_id=tag.id),
                group_id=tag.group_id,
                household_id=None,
                message=self.t("notifications.generic-deleted", name=tag.name),
            )

    @router.get("/slug/{tag_slug}", response_model=RecipeTagResponse)
    async def get_one_by_slug(self, tag_slug: str):
        return self.repo.get_one(tag_slug, "slug", override_schema=RecipeTagResponse)
