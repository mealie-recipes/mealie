from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from mealie.routes._base import BaseCrudController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema import mapper
from mealie.schema.recipe.recipe_tag_group import (
    TagGroupIn,
    TagGroupOut,
    TagGroupPagination,
    TagGroupSave,
    TagGroupSummary,
)
from mealie.schema.response.pagination import PaginationQuery

router = APIRouter(prefix="/tag-groups", tags=["Organizer: Tag Groups"])


@controller(router)
class TagGroupController(BaseCrudController):
    @cached_property
    def repo(self):
        return self.repos.tag_groups

    @cached_property
    def mixins(self):
        return HttpRepo(self.repo, self.logger)

    @router.get("", response_model=TagGroupPagination)
    async def get_all(self, q: PaginationQuery = Depends(PaginationQuery), search: str | None = None):
        """Returns a list of all tag groups for the current group"""
        response = self.repo.page_all(
            pagination=q,
            override=TagGroupOut,
            search=search,
        )
        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.get("/{item_id}", response_model=TagGroupSummary)
    def get_one(self, item_id: UUID4):
        """Returns a tag group with its associated tags"""
        return self.mixins.get_one(item_id)

    @router.post("", status_code=201, response_model=TagGroupOut)
    def create_one(self, tag_group: TagGroupIn):
        """Creates a new Tag Group"""
        save_data = mapper.cast(tag_group, TagGroupSave, group_id=self.group_id)
        return self.repo.create(save_data)

    @router.put("/{item_id}", response_model=TagGroupOut)
    def update_one(self, item_id: UUID4, tag_group: TagGroupIn):
        """Updates an existing Tag Group"""
        save_data = mapper.cast(tag_group, TagGroupSave, group_id=self.group_id)
        return self.repo.update(item_id, save_data)

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_one(self, item_id: UUID4):
        """
        Deletes a Tag Group. Tags that belong to the group will have their
        tag_group_id set to NULL (they become ungrouped) due to the ON DELETE SET NULL constraint.
        """
        try:
            self.repo.delete(item_id)
        except Exception as e:
            raise HTTPException(status.HTTP_400_BAD_REQUEST) from e

    @router.get("/slug/{tag_group_slug}", response_model=TagGroupSummary)
    async def get_one_by_slug(self, tag_group_slug: str):
        """Returns a tag group by slug"""
        return self.repo.get_one(tag_group_slug, "slug", override_schema=TagGroupSummary)
