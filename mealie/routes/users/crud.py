from fastapi import HTTPException, status
from fastapi.params import Depends
from pydantic import UUID4, BaseModel

from mealie.core.security import hash_password
from mealie.core.security.providers.credentials_provider import CredentialsProvider
from mealie.db.models.users.users import AuthMethod
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.routes.users._helpers import assert_user_change_allowed
from mealie.schema.response import ErrorResponse, SuccessResponse
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.user import ChangePassword, UserBase, UserOut
from mealie.schema.user.user import UserRatings, UserRatingSummary

user_router = UserAPIRouter(prefix="/users", tags=["Users: CRUD"])


class LoginHistoryQuery(PaginationQuery):
    user_id: UUID4 | None = None


class AddIpBlocklistIn(BaseModel):
    user_id: UUID4 | None = None
    ip_address: str
    reason: str | None = None


class DeleteIpBlocklistOut(BaseModel):
    user_id: UUID4 | None = None
    ip_address: str


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

    @user_router.put("/{item_id}")
    def update_user(self, item_id: UUID4, new_data: UserBase):
        assert_user_change_allowed(item_id, self.user, new_data)

        try:
            self.repos.users.update(item_id, new_data.model_dump())
        except Exception as e:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorResponse.respond("Failed to update user"),
            ) from e

        return SuccessResponse.respond(self.t("user.user-updated"))

    @user_router.get("/getLoginHistory")
    def get_login_history(self, q: LoginHistoryQuery = Depends(LoginHistoryQuery)):
        # if not admin, not allowed to search other user's record
        if q.user_id and q.user_id != self.user.id and not self.user.admin:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                ErrorResponse.respond("You do not have permission to view this user's login history"),
            )
        target_user_id = q.user_id
        if q.user_id:
            if not self.repos.users.get_one(target_user_id):
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    ErrorResponse.respond("User not found"),
                )
        else:
            target_user_id = self.user.id
        qf_part = f"user_id={target_user_id}"
        if q.query_filter:
            q.query_filter = f"({q.query_filter}) AND {qf_part}"
        else:
            q.query_filter = qf_part

        page_data = self.repos.login_history.page_all(pagination=q)
        ips = sorted({item.ip_address for item in page_data.items})
        if not ips:
            return page_data
        quoted_ips = ", ".join(f'"{ip}"' for ip in ips)

        block_filter = f"user_id={target_user_id} and ip_address in [{quoted_ips}]"
        blocked_rows = self.repos.userIpBlocklist.page_all(
            PaginationQuery(page=1, per_page=-1, query_filter=block_filter)
        ).items
        blocked_set = {row.ip_address for row in blocked_rows if row.ip_address}

        page_data.items = [
            item.model_copy(update={"is_blocked": bool(item.ip_address and item.ip_address in blocked_set)})
            for item in page_data.items
        ]
        return page_data

    @user_router.get("/self/ip-blocklist")
    def get_logged_in_user_ip_blocklist(self):
        return self.repos.userIpBlocklist.page_all(pagination=PaginationQuery(query_filter=f"user_id={self.user.id}"))

    @user_router.post("/self/ip-blocklist")
    def add_ip_to_blocklist(self, payload: AddIpBlocklistIn):
        target_user_id = payload.user_id or self.user.id

        # admin can block an ip to other's account. otherwise, user can only block an ip to his own account.
        if target_user_id != self.user.id and not self.user.admin:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                ErrorResponse.respond("You do not have permission to block IPs for this user"),
            )

        # no cross group：users repo is group scoped
        target_user = self.repos.users.get_one(target_user_id)
        if not target_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                ErrorResponse.respond("User not found"),
            )
        try:
            self.repos.userIpBlocklist.create(
                {
                    "user_id": target_user.id,
                    "ip_address": payload.ip_address,
                    "reason": payload.reason,
                    "created_by_user_id": self.user.id,
                }
            )
        except Exception as e:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, ErrorResponse.respond(f"Failed to add IP to blocklist. {str(e)}")
            ) from e
        return SuccessResponse.respond("IP address added to blocklist")

    @user_router.post("/self/remove-ip-blocklist")
    def remove_ip_from_blocklist(self, payload: DeleteIpBlocklistOut):
        target_user_id = payload.user_id or self.user.id

        # 允许 admin 代删；普通用户只能删自己
        if target_user_id != self.user.id and not self.user.admin:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                ErrorResponse.respond("You do not have permission to remove IP blocks for this user"),
            )

        # 同组约束：users repo 本身是 group scoped
        target_user = self.repos.users.get_one(target_user_id)
        if not target_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                ErrorResponse.respond("User not found"),
            )

        rows = self.repos.userIpBlocklist.multi_query(
            {"user_id": target_user.id, "ip_address": payload.ip_address},
            limit=100,  # 一般只会1条，防止历史脏数据
        )

        if not rows:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                ErrorResponse.respond("IP blocklist entry not found"),
            )

        self.repos.userIpBlocklist.delete_many([row.id for row in rows])

        return SuccessResponse.respond("IP address removed from blocklist")
