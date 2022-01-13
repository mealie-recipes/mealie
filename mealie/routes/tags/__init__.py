from functools import cached_property

from fastapi import APIRouter, HTTPException, status

from mealie.routes._base import BaseUserController, controller
from mealie.schema.recipe import RecipeTagResponse, TagIn

router = APIRouter(prefix="/tags", tags=["Tags: CRUD"])


@controller(router)
class TagController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.tags

    @router.get("")
    async def get_all_recipe_tags(self):
        """Returns a list of available tags in the database"""
        return self.repo.get_all_limit_columns(["slug", "name"])

    @router.get("/empty")
    def get_empty_tags(self):
        """Returns a list of tags that do not contain any recipes"""
        return self.repo.get_empty()

    @router.get("/{tag_slug}", response_model=RecipeTagResponse)
    def get_all_recipes_by_tag(self, tag_slug: str):
        """Returns a list of recipes associated with the provided tag."""
        return self.repo.get_one(tag_slug, override_schema=RecipeTagResponse)

    @router.post("", status_code=201)
    def create_recipe_tag(self, tag: TagIn):
        """Creates a Tag in the database"""
        return self.repo.create(tag)

    @router.put("/{tag_slug}", response_model=RecipeTagResponse)
    def update_recipe_tag(self, tag_slug: str, new_tag: TagIn):
        """Updates an existing Tag in the database"""
        return self.repo.update(tag_slug, new_tag)

    @router.delete("/{tag_slug}")
    def delete_recipe_tag(self, tag_slug: str):
        """Removes a recipe tag from the database. Deleting a
        tag does not impact a recipe. The tag will be removed
        from any recipes that contain it"""

        try:
            self.repo.delete(tag_slug)
        except Exception:
            raise HTTPException(status.HTTP_400_BAD_REQUEST)
