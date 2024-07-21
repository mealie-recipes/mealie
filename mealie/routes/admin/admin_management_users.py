from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from mealie.core import security
from mealie.routes._base import BaseAdminController, controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.response.responses import ErrorResponse
from mealie.schema.user.auth import UnlockResults
from mealie.schema.user.user import UserIn, UserOut, UserPagination
from mealie.schema.user.user_passwords import ForgotPassword, PasswordResetToken
from mealie.services.user_services.password_reset_service import PasswordResetService
from mealie.services.user_services.user_service import UserService

router = APIRouter(prefix="/users")


@controller(router)
class AdminUserManagementRoutes(BaseAdminController):
    @cached_property
    def repo(self):
        return self.repos.users

    # =======================================================================
    # CRUD Operations

    @property
    def mixins(self):
        return HttpRepo[UserIn, UserOut, UserOut](self.repo, self.logger, self.registered_exceptions)

    @router.get("", response_model=UserPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repo.page_all(
            pagination=q,
            override=UserOut,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=UserOut, status_code=201)
    def create_one(self, data: UserIn):
        data.password = security.hash_password(data.password)
        return self.mixins.create_one(data)

    @router.post("/unlock", response_model=UnlockResults)
    def unlock_users(self, force: bool = False) -> UnlockResults:
        user_service = UserService(self.repos)
        unlocked = user_service.reset_locked_users(force=force)

        return UnlockResults(unlocked=unlocked)

    @router.get("/{item_id}", response_model=UserOut)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=UserOut)
    def update_one(self, item_id: UUID4, data: UserOut):
        # Prevent self demotion
        if self.user.id == item_id and self.user.admin != data.admin:
            raise HTTPException(status_code=403, detail=ErrorResponse.respond("you cannot demote yourself"))

        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=UserOut)
    def delete_one(self, item_id: UUID4):
        return self.mixins.delete_one(item_id)

    @router.post("/password-reset-token", response_model=PasswordResetToken, status_code=201)
    def generate_token(self, email: ForgotPassword):
        """Generates a reset token and returns it. This is an authenticated endpoint"""
        f_service = PasswordResetService(self.session)
        token_entry = f_service.generate_reset_token(email.email)
        if not token_entry:
            raise HTTPException(status_code=500, detail=ErrorResponse.respond("error while generating reset token"))
        return PasswordResetToken(token=token_entry.token)
