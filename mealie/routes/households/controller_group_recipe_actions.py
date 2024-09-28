from functools import cached_property

import requests
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4

from mealie.core.exceptions import NoEntryFound
from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema.household.group_recipe_action import (
    CreateGroupRecipeAction,
    GroupRecipeActionOut,
    GroupRecipeActionPagination,
    GroupRecipeActionPayload,
    GroupRecipeActionType,
    SaveGroupRecipeAction,
)
from mealie.schema.response import ErrorResponse
from mealie.schema.response.pagination import PaginationQuery
from mealie.services.recipe.recipe_service import RecipeService

router = APIRouter(prefix="/households/recipe-actions", tags=["Households: Recipe Actions"])


@controller(router)
class GroupRecipeActionController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.group_recipe_actions

    @property
    def mixins(self):
        return HttpRepo[CreateGroupRecipeAction, GroupRecipeActionOut, SaveGroupRecipeAction](self.repo, self.logger)

    # ==================================================================================================================
    # CRUD

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

    # ==================================================================================================================
    # Actions

    @router.post("/{item_id}/trigger/{recipe_slug}", status_code=202)
    def trigger_action(self, item_id: UUID4, recipe_slug: str, bg_tasks: BackgroundTasks) -> None:
        recipe_action = self.repos.group_recipe_actions.get_one(item_id)
        if not recipe_action:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse.respond(message="Not found."),
            )

        if recipe_action.action_type == GroupRecipeActionType.post.value:
            task_action = requests.post
        else:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse.respond(message=f'Cannot trigger action type "{recipe_action.action_type}".'),
            )

        recipe_service = RecipeService(self.repos, self.user, self.household, translator=self.translator)
        try:
            recipe = recipe_service.get_one(recipe_slug)
        except NoEntryFound as e:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse.respond(message="Not found."),
            ) from e

        payload = GroupRecipeActionPayload(action=recipe_action, content=recipe)
        bg_tasks.add_task(
            task_action,
            url=recipe_action.url,
            json=jsonable_encoder(payload.model_dump()),
            timeout=15,
        )
