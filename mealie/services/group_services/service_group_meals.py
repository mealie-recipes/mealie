import random

from pydantic import UUID4

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import Recipe, RecipeCategory
from mealie.services._base_service import BaseService


class MealPlanService(BaseService):
    def __init__(self, group_id: UUID4, repos: AllRepositories):
        self.group_id = group_id
        self.repos = repos

    def get_random_recipe(self, categories: list[RecipeCategory] = None) -> Recipe:
        """get_random_recipe returns a single recipe matching a specific criteria of
        categories. if no categories are provided, a single recipe is returned from the
        entire recipe databas.

        Note that the recipe must contain ALL categories in the list provided.

        Args:
            categories (list[RecipeCategory], optional): [description]. Defaults to None.

        Returns:
            Recipe: [description]
        """
        recipes = self.repos.recipes.by_group(self.group_id).get_by_categories(categories)
        return random.choice(recipes)
