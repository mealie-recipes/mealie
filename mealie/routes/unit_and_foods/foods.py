from functools import cached_property

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.db.models.household.shopping_list import ShoppingList, ShoppingListItem
from mealie.db.models.recipe.ingredient import RecipeIngredientModel
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.routers import MealieCrudRoute
from mealie.schema import mapper
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFood,
    IngredientFood,
    IngredientFoodPagination,
    MergeFood,
    SaveIngredientFood,
)
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.response.responses import SuccessResponse
from mealie.services.household_services.shopping_lists import ShoppingListService
from mealie.services.recipe.recipe_service import RecipeService

router = APIRouter(prefix="/foods", tags=["Recipes: Foods"], route_class=MealieCrudRoute)


@controller(router)
class IngredientFoodsController(BaseUserController):
    @cached_property
    def repo(self):
        return self.repos.ingredient_foods

    @cached_property
    def mixins(self):
        return HttpRepo[SaveIngredientFood, IngredientFood, CreateIngredientFood](
            self.repo,
            self.logger,
            self.registered_exceptions,
        )

    @router.get("", response_model=IngredientFoodPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery), search: str | None = None):
        response = self.repo.page_all(
            pagination=q,
            override=IngredientFood,
            search=search,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=IngredientFood, status_code=201)
    def create_one(self, data: CreateIngredientFood):
        self.checks.can_organize()
        save_data = mapper.cast(data, SaveIngredientFood, group_id=self.group_id)
        return self.mixins.create_one(save_data)

    @router.put("/merge", response_model=SuccessResponse)
    def merge_one(self, data: MergeFood):
        self.checks.can_organize()
        try:
            self.repo.merge(data.from_food, data.to_food)
            return SuccessResponse.respond("Successfully merged foods")
        except Exception as e:
            self.logger.error(e)
            raise HTTPException(500, "Failed to merge foods") from e

    @router.get("/{item_id}", response_model=IngredientFood)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=IngredientFood)
    def update_one(self, item_id: UUID4, data: CreateIngredientFood):
        self.checks.can_organize()
        data = mapper.cast(data, SaveIngredientFood, group_id=self.group_id)
        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=IngredientFood)
    def delete_one(self, item_id: UUID4):
        self.checks.can_organize()
        self._repair_recipes(item_id)
        self._repair_shopping_lists(item_id)

        return self.mixins.delete_one(item_id)

    def _repair_recipes(self, item_id: UUID4):
        recipe_service = RecipeService(self.repos, self.user, self.household, translator=self.translator)
        fltr = RecipeModel.recipe_ingredient.any(RecipeIngredientModel.food_id == item_id)
        query = sa.select(RecipeModel).filter(RecipeModel.household_id.is_not(None)).filter(fltr)
        recipes = self.session.execute(query).scalars().unique().all()
        for recipe_model in recipes:
            recipe = recipe_service.get_one(recipe_model.id)
            for ingredient in recipe.recipe_ingredient:
                if ingredient.food is None or not ingredient.food.id == item_id:
                    continue
                ingredient.note = f"{ingredient.food.name} {ingredient.note}"
            recipe_service.update_one(recipe_model.id, recipe)

    def _repair_shopping_lists(self, item_id: UUID4):
        service = ShoppingListService(self.repos)
        fltr = ShoppingList.list_items.any(ShoppingListItem.food_id == item_id)
        query = sa.select(ShoppingList).filter(ShoppingList.household_id.is_not(None)).filter(fltr)
        lists = self.session.execute(query).scalars().unique().all()
        for list_model in lists:
            for item_model in list_model.list_items:
                if item_model.food is None or not item_model.food.id == item_id:
                    continue
                item = service.list_items.get_one(item_model.id, "id")
                if item is None or item.food is None:
                    continue
                item.note = f"{item.food.name} {item.note}"
                service.list_items.update(item_model.id, item)
