from fastapi import Depends, HTTPException, status
from pydantic import UUID4

from mealie.core.security import hash_password, verify_password
from mealie.routes._base import BaseAdminController, BaseUserController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.routers import AdminAPIRouter, UserAPIRouter
from mealie.routes.users._helpers import assert_user_change_allowed
from mealie.schema.response import ErrorResponse, SuccessResponse
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.user import ChangePassword, UserBase, UserIn, UserOut
from mealie.schema.user.user import UserPagination

user_router = UserAPIRouter(prefix="/users", tags=["Users: CRUD"])
admin_router = AdminAPIRouter(prefix="/users", tags=["Users: Admin CRUD"])


@controller(admin_router)
class AdminUserController(BaseAdminController):
    @property
    def mixins(self) -> HttpRepo:
        return HttpRepo[UserIn, UserOut, UserBase](self.repos.users, self.logger)

    @admin_router.get("", response_model=UserPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repos.users.page_all(
            pagination=q,
            override=UserOut,
        )

        response.set_pagination_guides(admin_router.url_path_for("get_all"), q.dict())
        return response

    @admin_router.post("", response_model=UserOut, status_code=201)
    def create_user(self, new_user: UserIn):
        new_user.password = hash_password(new_user.password)
        return self.mixins.create_one(new_user)

    @admin_router.get("/{item_id}", response_model=UserOut)
    def get_user(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @admin_router.delete("/{item_id}")
    def delete_user(self, item_id: UUID4):
        """Removes a user from the database. Must be the current user or a super user"""

        assert_user_change_allowed(item_id, self.user)

        if item_id == 1:  # TODO: identify super_user
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="SUPER_USER")

        self.mixins.delete_one(item_id)


@controller(user_router)
class UserController(BaseUserController):
    @user_router.get("/self", response_model=UserOut)
    def get_logged_in_user(self):
        return self.user

    @user_router.put("/password")
    def update_password(self, password_change: ChangePassword):
        """Resets the User Password"""
        if not verify_password(password_change.current_password, self.user.password):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, ErrorResponse.respond("Invalid current password"))

        self.user.password = hash_password(password_change.new_password)
        try:
            self.repos.users.update_password(self.user.id, self.user.password)
        except Exception as e:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorResponse.respond("Failed to update password"),
            ) from e

        return SuccessResponse.respond("Password updated")

    @user_router.put("/{item_id}")
    def update_user(self, item_id: UUID4, new_data: UserBase):
        assert_user_change_allowed(item_id, self.user)

        if not self.user.admin and (new_data.admin or self.user.group != new_data.group):
            # prevent a regular user from doing admin tasks on themself
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, ErrorResponse.respond("User doesn't have permission to change group")
            )

        if self.user.id == item_id and self.user.admin and not new_data.admin:
            # prevent an admin from demoting themself
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, ErrorResponse.respond("User doesn't have permission to change group")
            )

        try:
            self.repos.users.update(item_id, new_data.dict())
        except Exception as e:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorResponse.respond("Failed to update user"),
            ) from e

        return SuccessResponse.respond("User updated")
