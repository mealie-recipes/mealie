from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.routes._base.abc_controller import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import CrudMixins
from mealie.schema import mapper
from mealie.schema.query import GetAll
from mealie.schema.recipe.recipe_ingredient import CreateIngredientFood, IngredientFood, MergeFood, SaveIngredientFood
from mealie.schema.response.responses import SuccessResponse

router = APIRouter(prefix="/foods", tags=["Recipes: Foods"])


@controller(router)
class IngredientFoodsController(BaseUserController):
    @cached_property
    def repo(self):
        return self.deps.repos.ingredient_foods.by_group(self.group_id)

    @cached_property
    def mixins(self):
        return CrudMixins[SaveIngredientFood, IngredientFood, CreateIngredientFood](
            self.repo,
            self.deps.logger,
            self.registered_exceptions,
        )

    @router.put("/merge", response_model=SuccessResponse)
    def merge_one(self, data: MergeFood):
        try:
            self.repo.merge(data.from_food, data.to_food)
            return SuccessResponse.respond("Successfully merged foods")
        except Exception as e:
            self.deps.logger.error(e)
            raise HTTPException(500, "Failed to merge foods") from e

    @router.get("", response_model=list[IngredientFood])
    def get_all(self, q: GetAll = Depends(GetAll)):
        return self.repo.get_all(start=q.start, limit=q.limit)

    @router.post("", response_model=IngredientFood, status_code=201)
    def create_one(self, data: CreateIngredientFood):
        save_data = mapper.cast(data, SaveIngredientFood, group_id=self.group_id)
        return self.mixins.create_one(save_data)

    @router.get("/{item_id}", response_model=IngredientFood)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=IngredientFood)
    def update_one(self, item_id: UUID4, data: CreateIngredientFood):
        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=IngredientFood)
    def delete_one(self, item_id: UUID4):
        return self.mixins.delete_one(item_id)
