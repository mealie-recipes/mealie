from pydantic import UUID4

from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.routes.users._helpers import assert_user_change_allowed
from mealie.schema.user import UserFavorites

router = UserAPIRouter()


@controller(router)
class UserFavoritesController(BaseUserController):
    @router.get("/{id}/favorites", response_model=UserFavorites)
    async def get_favorites(self, id: UUID4):
        """Get user's favorite recipes"""
        return self.repos.users.get(id, override_schema=UserFavorites)

    @router.post("/{id}/favorites/{slug}")
    def add_favorite(self, id: UUID4, slug: str):
        """Adds a Recipe to the users favorites"""
        assert_user_change_allowed(id, self.user)
        self.user.favorite_recipes.append(slug)
        self.repos.users.update(self.user.id, self.user)

    @router.delete("/{id}/favorites/{slug}")
    def remove_favorite(self, id: UUID4, slug: str):
        """Adds a Recipe to the users favorites"""
        assert_user_change_allowed(id, self.user)
        self.user.favorite_recipes = [x for x in self.user.favorite_recipes if x != slug]
        self.repos.users.update(self.user.id, self.user)
        return
