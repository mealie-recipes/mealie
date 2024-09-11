from functools import cached_property
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import UUID4

from mealie.repos.all_repositories import get_repositories
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.routes.users._helpers import assert_user_change_allowed
from mealie.schema.response.responses import ErrorResponse
from mealie.schema.user.user import UserRatingCreate, UserRatingOut, UserRatings, UserRatingUpdate

router = UserAPIRouter()


@controller(router)
class UserRatingsController(BaseUserController):
    @cached_property
    def group_recipes(self):
        return get_repositories(self.session, group_id=self.group_id, household_id=None).recipes

    def get_recipe_or_404(self, slug_or_id: str | UUID):
        """Fetches a recipe by slug or id, or raises a 404 error if not found."""
        if isinstance(slug_or_id, str):
            try:
                slug_or_id = UUID(slug_or_id)
            except ValueError:
                pass

        if isinstance(slug_or_id, UUID):
            recipe = self.group_recipes.get_one(slug_or_id, key="id")
        else:
            recipe = self.group_recipes.get_one(slug_or_id, key="slug")

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
    def set_rating(self, id: UUID4, slug: str, data: UserRatingUpdate):
        """Sets the user's rating for a recipe"""
        assert_user_change_allowed(id, self.user)

        recipe = self.get_recipe_or_404(slug)
        user_rating = self.repos.user_ratings.get_by_user_and_recipe(id, recipe.id)
        if not user_rating:
            self.repos.user_ratings.create(
                UserRatingCreate(
                    user_id=id,
                    recipe_id=recipe.id,
                    rating=data.rating,
                    is_favorite=data.is_favorite or False,
                )
            )
        else:
            if data.rating is not None:
                user_rating.rating = data.rating
            if data.is_favorite is not None:
                user_rating.is_favorite = data.is_favorite

            self.repos.user_ratings.update(user_rating.id, user_rating)

    @router.post("/{id}/favorites/{slug}")
    def add_favorite(self, id: UUID4, slug: str):
        """Adds a recipe to the user's favorites"""
        self.set_rating(id, slug, data=UserRatingUpdate(is_favorite=True))

    @router.delete("/{id}/favorites/{slug}")
    def remove_favorite(self, id: UUID4, slug: str):
        """Removes a recipe from the user's favorites"""
        self.set_rating(id, slug, data=UserRatingUpdate(is_favorite=False))
