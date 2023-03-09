from pydantic import UUID4
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.group.shopping_list import ShoppingList, ShoppingListRecipeReference
from mealie.schema.group.group_shopping_list import ShoppingListOut, ShoppingListUpdate

from .repository_generic import RepositoryGeneric
from ..db.models.recipe import RecipeModel


class RepositoryShoppingList(RepositoryGeneric[ShoppingListOut, ShoppingList]):
    def update(self, item_id: UUID4, data: ShoppingListUpdate) -> ShoppingListOut:  # type: ignore
        return super().update(item_id, data)

    def paging_query_options(self) -> list[LoaderOption]:
        return [
            joinedload(ShoppingList.extras),
            joinedload(ShoppingList.recipe_references)
            .joinedload(ShoppingListRecipeReference.recipe)
            .joinedload(RecipeModel.recipe_category),
            joinedload(ShoppingList.recipe_references)
            .joinedload(ShoppingListRecipeReference.recipe)
            .joinedload(RecipeModel.tags),
            joinedload(ShoppingList.recipe_references)
            .joinedload(ShoppingListRecipeReference.recipe)
            .joinedload(RecipeModel.tools),
            joinedload(ShoppingList.label_settings),
        ]
