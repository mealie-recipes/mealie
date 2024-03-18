from uuid import UUID

from fastapi import HTTPException, status
from pydantic import UUID4

from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.routes.users._helpers import assert_user_change_allowed
from mealie.schema.response.responses import ErrorResponse
from mealie.schema.user.user import UserRatingCreate, UserRatingOut, UserRatings

router = UserAPIRouter()


@controller(router)
class UserRatingsController(BaseUserController):
    def get_recipe_or_404(self, slug_or_id: str | UUID):
        """Fetches a recipe by slug or id, or raises a 404 error if not found."""
        if isinstance(slug_or_id, str):
            try:
                slug_or_id = UUID(slug_or_id)
            except ValueError:
                pass

        if isinstance(slug_or_id, UUID):
            recipe = self.repos.recipes.get_one(slug_or_id, key="id")
        else:
            recipe = self.repos.recipes.get_one(slug_or_id, key="slug")

        if not recipe:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse.respond(message="Not found."),
            )

        return recipe

    @router.get("/{id}/ratings", response_model=UserRatings[UserRatingOut])
    async def get_ratings(self, id: UUID4):
        """Get user's rated recipes"""
        return UserRatings(ratings=self.repos.user_ratings.get_by_user(id))

    @router.get("/{id}/favorites", response_model=UserRatings[UserRatingOut])
    async def get_favorites(self, id: UUID4):
        """Get user's favorited recipes"""
        return UserRatings(ratings=self.repos.user_ratings.get_by_user(id, favorites_only=True))

    @router.post("/{id}/ratings/{slug}")
    def set_rating(self, id: UUID4, slug: str, rating: float | None = None, is_favorite: bool | None = None):
        """Sets the user's rating for a recipe"""
        assert_user_change_allowed(id, self.user)

        recipe = self.get_recipe_or_404(slug)
        user_rating = self.repos.user_ratings.get_by_user_and_recipe(id, recipe.id)
        if not user_rating:
            self.repos.user_ratings.create(
                UserRatingCreate(
                    user_id=id,
                    recipe_id=recipe.id,
                    rating=rating,
                    is_favorite=is_favorite or False,
                )
            )
        else:
            if rating is not None:
                user_rating.rating = rating
            if is_favorite is not None:
                user_rating.is_favorite = is_favorite

            self.repos.user_ratings.update(user_rating.id, user_rating)

    @router.post("/{id}/favorites/{slug}")
    def add_favorite(self, id: UUID4, slug: str):
        """Adds a Recipe to the user's favorites"""
        self.set_rating(id, slug, is_favorite=True)

    @router.delete("/{id}/favorites/{slug}")
    def remove_favorite(self, id: UUID4, slug: str):
        """Adds a Recipe to the user's favorites"""
        self.set_rating(id, slug, is_favorite=False)
