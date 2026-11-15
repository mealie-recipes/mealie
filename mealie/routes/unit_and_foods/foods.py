from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.permissions import Perm, require
from mealie.routes._base.routers import MealieCrudRoute
from mealie.schema import mapper
from mealie.schema.recipe.recipe_ingredient import (
    IngredientFoodCreate,
    IngredientFoodMerge,
    IngredientFoodOut,
    IngredientFoodPagination,
    IngredientFoodSave,
)
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.response.responses import SuccessResponse

router = APIRouter(prefix="/foods", tags=["Recipes: Foods"], route_class=MealieCrudRoute)


@controller(router)
class IngredientFoodsController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.ingredient_foods

    @cached_property
    def mixins(self):
        return HttpRepo[IngredientFoodSave, IngredientFoodOut, IngredientFoodCreate](
            self.repo,
            self.logger,
            self.registered_exceptions,
        )

    @router.get("", response_model=IngredientFoodPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery), search: str | None = None):
        response = self.repo.page_all(
            pagination=q,
            override=IngredientFoodOut,
            search=search,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=IngredientFoodOut, status_code=201, dependencies=[require(Perm.GROUP_ORGANIZE)])
    def create_one(self, data: IngredientFoodCreate):
        save_data = mapper.cast(data, IngredientFoodSave, group_id=self.group_id)
        return self.mixins.create_one(save_data)

    @router.get("/empty", response_model=list[IngredientFoodOut])
    def get_all_empty(self):
        """Returns a list of foods that are not used by any recipe"""
        return self.repo.get_empty()

    @router.put("/merge", response_model=SuccessResponse, dependencies=[require(Perm.GROUP_ORGANIZE)])
    def merge_one(self, data: IngredientFoodMerge):
        try:
            self.repo.merge(data.from_food, data.to_food)
            return SuccessResponse.respond("Successfully merged foods")
        except Exception as e:
            self.logger.error(e)
            raise HTTPException(500, "Failed to merge foods") from e

    @router.get("/{item_id}", response_model=IngredientFoodOut)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=IngredientFoodOut, dependencies=[require(Perm.GROUP_ORGANIZE)])
    def update_one(self, item_id: UUID4, data: IngredientFoodCreate):
        data = mapper.cast(data, IngredientFoodSave, group_id=self.group_id)
        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=IngredientFoodOut, dependencies=[require(Perm.GROUP_ORGANIZE)])
    def delete_one(self, item_id: UUID4):
        return self.mixins.delete_one(item_id)
