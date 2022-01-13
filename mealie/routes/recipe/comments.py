from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.recipe.recipe_comments import RecipeCommentOut

router = UserAPIRouter()


@controller(router)
class RecipeCommentsController(BaseUserController):
    @router.get("/{slug}/comments", response_model=list[RecipeCommentOut])
    async def get_recipe_comments(self, slug: str):
        """Get all comments for a recipe"""
        recipe = self.repos.recipes.by_group(self.group_id).get_one(slug)
        return self.repos.comments.multi_query({"recipe_id": recipe.id})
