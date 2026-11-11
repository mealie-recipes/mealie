from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BasePublicGroupExploreController
from mealie.schema.make_dependable import make_dependable
from mealie.schema.recipe.recipe_ingredient import IngredientFoodOut
from mealie.schema.response.pagination import PaginationBase, PaginationQuery

router = APIRouter(prefix="/foods")


@controller(router)
class PublicFoodsController(BasePublicGroupExploreController):
    @property
    def ingredient_foods(self):
        return self.repos.ingredient_foods

    @router.get("", response_model=PaginationBase[IngredientFoodOut])
    def get_all(
        self,
        q: PaginationQuery = Depends(make_dependable(PaginationQuery)),
        search: str | None = None,
    ) -> PaginationBase[IngredientFoodOut]:
        response = self.ingredient_foods.page_all(
            pagination=q,
            override=IngredientFoodOut,
            search=search,
        )

        response.set_pagination_guides(self.get_explore_url_path(router.url_path_for("get_all")), q.model_dump())
        return response

    @router.get("/{item_id}", response_model=IngredientFoodOut)
    def get_one(self, item_id: UUID4) -> IngredientFoodOut:
        item = self.ingredient_foods.get_one(item_id)
        if not item:
            raise HTTPException(404, "food not found")

        return item
