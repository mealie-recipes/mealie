from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.routers import MealieCrudRoute
from mealie.schema import mapper
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientUnit,
    IngredientUnit,
    IngredientUnitPagination,
    MergeUnit,
    SaveIngredientUnit,
)
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.response.responses import SuccessResponse

router = APIRouter(prefix="/units", tags=["Recipes: Units"], route_class=MealieCrudRoute)


@controller(router)
class IngredientUnitsController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.ingredient_units

    @cached_property
    def mixins(self):
        return HttpRepo[CreateIngredientUnit, IngredientUnit, CreateIngredientUnit](
            self.repo,
            self.logger,
            self.registered_exceptions,
        )

    @router.get("", response_model=IngredientUnitPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery), search: str | None = None):
        response = self.repo.page_all(
            pagination=q,
            override=IngredientUnit,
            search=search,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=IngredientUnit, status_code=201)
    def create_one(self, data: CreateIngredientUnit):
        save_data = mapper.cast(data, SaveIngredientUnit, group_id=self.group_id)
        return self.mixins.create_one(save_data)

    @router.put("/merge", response_model=SuccessResponse)
    def merge_one(self, data: MergeUnit):
        try:
            self.repo.merge(data.from_unit, data.to_unit)
            return SuccessResponse.respond("Successfully merged units")
        except Exception as e:
            self.logger.error(e)
            raise HTTPException(500, "Failed to merge units") from e

    @router.get("/{item_id}", response_model=IngredientUnit)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=IngredientUnit)
    def update_one(self, item_id: UUID4, data: CreateIngredientUnit):
        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=IngredientUnit)
    def delete_one(self, item_id: UUID4):
        return self.mixins.delete_one(item_id)  # type: ignore
