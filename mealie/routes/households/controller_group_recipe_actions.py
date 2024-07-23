from functools import cached_property

from fastapi import APIRouter, Depends
from pydantic import UUID4

from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema.household.group_recipe_action import (
    CreateGroupRecipeAction,
    GroupRecipeActionOut,
    GroupRecipeActionPagination,
    SaveGroupRecipeAction,
)
from mealie.schema.response.pagination import PaginationQuery

router = APIRouter(prefix="/households/recipe-actions", tags=["Households: Recipe Actions"])


@controller(router)
class GroupRecipeActionController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.group_recipe_actions

    @property
    def mixins(self):
        return HttpRepo[CreateGroupRecipeAction, GroupRecipeActionOut, SaveGroupRecipeAction](self.repo, self.logger)

    @router.get("", response_model=GroupRecipeActionPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repo.page_all(
            pagination=q,
            override=GroupRecipeActionOut,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=GroupRecipeActionOut, status_code=201)
    def create_one(self, data: CreateGroupRecipeAction):
        save = data.cast(SaveGroupRecipeAction, group_id=self.group_id, household_id=self.household_id)
        return self.mixins.create_one(save)

    @router.get("/{item_id}", response_model=GroupRecipeActionOut)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=GroupRecipeActionOut)
    def update_one(self, item_id: UUID4, data: SaveGroupRecipeAction):
        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=GroupRecipeActionOut)
    def delete_one(self, item_id: UUID4):
        return self.mixins.delete_one(item_id)
