from fastapi import HTTPException, status
from pydantic import UUID4

from mealie.core.security import hash_password
from mealie.core.security.providers.credentials_provider import CredentialsProvider
from mealie.db.models.users.users import AuthMethod
from mealie.repos.all_repositories import get_repositories
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.routes.users._helpers import assert_user_change_allowed
from mealie.schema.response import ErrorResponse, SuccessResponse
from mealie.schema.user import ChangePassword, DeleteSelf, UserBase, UserOut
from mealie.schema.user.user import UserRatings, UserRatingSummary, UserSelfUpdate

user_router = UserAPIRouter(prefix="/users", tags=["Users: CRUD"])


@controller(user_router)
class UserController(BaseUserController):
    @user_router.get("/self", response_model=UserOut)
    def get_logged_in_user(self):
        return self.user

    @user_router.get("/self/ratings", response_model=UserRatings[UserRatingSummary])
    def get_logged_in_user_ratings(self):
        return UserRatings(ratings=self.repos.user_ratings.get_by_user(self.user.id))

    @user_router.get("/self/ratings/{recipe_id}", response_model=UserRatingSummary)
    def get_logged_in_user_rating_for_recipe(self, recipe_id: UUID4):
        user_rating = self.repos.user_ratings.get_by_user_and_recipe(self.user.id, recipe_id)
        if user_rating:
            return user_rating
        else:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                ErrorResponse.respond("User has not rated this recipe"),
            )

    @user_router.get("/self/favorites", response_model=UserRatings[UserRatingSummary])
    def get_logged_in_user_favorites(self):
        return UserRatings(ratings=self.repos.user_ratings.get_by_user(self.user.id, favorites_only=True))

    @user_router.put("/password")
    def update_password(self, password_change: ChangePassword):
        """Resets the User Password"""
        if self.user.auth_method == AuthMethod.LDAP:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, ErrorResponse.respond(self.t("user.ldap-update-password-unavailable"))
            )
        if not CredentialsProvider.verify_password(password_change.current_password, self.user.password):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, ErrorResponse.respond(self.t("user.invalid-current-password"))
            )

        self.user.password = hash_password(password_change.new_password)
        try:
            self.repos.users.update_password(self.user.id, self.user.password)
        except Exception as e:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorResponse.respond("Failed to update password"),
            ) from e

        return SuccessResponse.respond(self.t("user.password-updated"))

    @user_router.delete("/self")
    def delete_self(self, data: DeleteSelf):
        """Permanently deletes the logged-in user's own account (GDPR right to erasure)."""
        if self.user.auth_method != AuthMethod.LDAP and not CredentialsProvider.verify_password(
            data.current_password, self.user.password
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, ErrorResponse.respond(self.t("user.invalid-current-password"))
            )

        if self.user.admin:
            # Instance-wide, not scoped to this user's group - admin is a superuser flag.
            all_users = get_repositories(self.session, group_id=None, household_id=None).users.get_all()
            if sum(1 for u in all_users if u.admin) <= 1:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, ErrorResponse.respond(self.t("user.cannot-delete-last-admin"))
                )

        self.repos.users.delete(self.user.id)
        return SuccessResponse.respond(self.t("user.account-deleted"))

    @user_router.put("/{item_id}")
    def update_user(self, item_id: UUID4, new_data: UserBase):
        # assert_user_change_allowed inspects the full submitted data, so permission-escalation
        # attempts still get a 403 exactly as before. On top of that, as defense-in-depth, only
        # fields in UserSelfUpdate are ever actually persisted - admin/permission/group/household
        # always come from the caller's own current record, never from the request body, even if
        # the equality check above had a bug.
        assert_user_change_allowed(item_id, self.user, new_data)

        safe_update = UserSelfUpdate.model_validate(new_data.model_dump())
        merged = UserBase(**self.user.model_dump()).model_copy(update=safe_update.model_dump(exclude_unset=True))

        try:
            self.repos.users.update(item_id, merged.model_dump())
        except Exception as e:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorResponse.respond("Failed to update user"),
            ) from e

        return SuccessResponse.respond(self.t("user.user-updated"))
