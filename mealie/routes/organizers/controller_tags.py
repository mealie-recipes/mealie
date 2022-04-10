from functools import cached_property

from fastapi import APIRouter, HTTPException, status
from pydantic import UUID4

from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema import mapper
from mealie.schema.recipe import RecipeTagResponse, TagIn
from mealie.schema.recipe.recipe import RecipeTag
from mealie.schema.recipe.recipe_category import TagSave

router = APIRouter(prefix="/tags", tags=["Organizer: Tags"])


@controller(router)
class TagController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.tags.by_group(self.group_id)

    @cached_property
    def mixins(self):
        return HttpRepo(self.repo, self.deps.logger)

    @router.get("")
    async def get_all(self):
        """Returns a list of available tags in the database"""
        return self.repo.get_all(override_schema=RecipeTag)

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
        return self.repo.create(save_data)

    @router.put("/{item_id}", response_model=RecipeTagResponse)
    def update_one(self, item_id: UUID4, new_tag: TagIn):
        """Updates an existing Tag in the database"""
        save_data = mapper.cast(new_tag, TagSave, group_id=self.group_id)
        return self.repo.update(item_id, save_data)

    @router.delete("/{item_id}")
    def delete_recipe_tag(self, item_id: UUID4):
        """Removes a recipe tag from the database. Deleting a
        tag does not impact a recipe. The tag will be removed
        from any recipes that contain it"""

        try:
            self.repo.delete(item_id)
        except Exception as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST) from e

    @router.get("/slug/{tag_slug}", response_model=RecipeTagResponse)
    async def get_one_by_slug(self, tag_slug: str):
        return self.repo.get_one(tag_slug, "slug", override_schema=RecipeTagResponse)
