from functools import cached_property

from fastapi import APIRouter, Depends

from mealie.routes._base.abc_controller import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import CrudMixins
from mealie.schema.query import GetAll
from mealie.schema.recipe.recipe_ingredient import CreateIngredientFood, IngredientFood

router = APIRouter(prefix="/foods", tags=["Recipes: Foods"])


@controller(router)
class IngredientFoodsController(BaseUserController):
    @cached_property
    def repo(self):
        return self.deps.repos.ingredient_foods

    @cached_property
    def mixins(self):
        return CrudMixins[CreateIngredientFood, IngredientFood, CreateIngredientFood](
            self.repo,
            self.deps.logger,
            self.registered_exceptions,
        )

    @router.get("", response_model=list[IngredientFood])
    def get_all(self, q: GetAll = Depends(GetAll)):
        return self.repo.get_all(start=q.start, limit=q.limit)

    @router.post("", response_model=IngredientFood, status_code=201)
    def create_one(self, data: CreateIngredientFood):
        return self.mixins.create_one(data)

    @router.get("/{item_id}", response_model=IngredientFood)
    def get_one(self, item_id: int):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=IngredientFood)
    def update_one(self, item_id: int, data: CreateIngredientFood):
        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=IngredientFood)
    def delete_one(self, item_id: int):
        return self.mixins.delete_one(item_id)
