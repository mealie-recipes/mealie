from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.routes._base import controller
from mealie.routes._base.base_controllers import BasePublicExploreController
from mealie.schema.make_dependable import make_dependable
from mealie.schema.recipe.recipe_ingredient import IngredientFood
from mealie.schema.response.pagination import PaginationBase, PaginationQuery

router = APIRouter(prefix="/foods/{group_slug}")


@controller(router)
class PublicFoodsController(BasePublicExploreController):
    @property
    def ingredient_foods(self):
        return self.repos.ingredient_foods.by_group(self.group.id)

    @router.get("", response_model=PaginationBase[IngredientFood])
    def get_all(
        self, q: PaginationQuery = Depends(make_dependable(PaginationQuery)), search: str | None = None
    ) -> PaginationBase[IngredientFood]:
        response = self.ingredient_foods.page_all(
            pagination=q,
            override=IngredientFood,
            search=search,
        )

        response.set_pagination_guides(router.url_path_for("get_all", group_slug=self.group.slug), q.model_dump())
        return response

    @router.get("/{item_id}", response_model=IngredientFood)
    def get_one(self, item_id: UUID4) -> IngredientFood:
        item = self.ingredient_foods.get_one(item_id)
        if not item:
            raise HTTPException(404, "food not found")

        return item
