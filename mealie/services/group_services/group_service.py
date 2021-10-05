from __future__ import annotations

from uuid import uuid4

from fastapi import Depends, HTTPException, status

from mealie.core.dependencies.grouped import UserDeps
from mealie.core.root_logger import get_logger
from mealie.schema.group.group_permissions import SetPermissions
from mealie.schema.group.group_preferences import UpdateGroupPreferences
from mealie.schema.group.invite_token import EmailInitationResponse, EmailInvitation, ReadInviteToken, SaveInviteToken
from mealie.schema.recipe.recipe_category import CategoryBase
from mealie.schema.user.user import GroupInDB, PrivateUser, UserOut
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.email import EmailService
from mealie.services.events import create_group_event

logger = get_logger(module=__name__)


class GroupSelfService(UserHttpService[int, str]):
    _restrict_by_group = False
    event_func = create_group_event
    item: GroupInDB

    @classmethod
    def read_existing(cls, deps: UserDeps = Depends()):
        """Override parent method to remove `item_id` from arguments"""
        return super().read_existing(item_id=0, deps=deps)

    @classmethod
    def write_existing(cls, deps: UserDeps = Depends()):
        """Override parent method to remove `item_id` from arguments"""
        return super().write_existing(item_id=0, deps=deps)

    @classmethod
    def manage_existing(cls, deps: UserDeps = Depends()):
        """Override parent method to remove `item_id` from arguments"""
        if not deps.user.can_manage:
            raise HTTPException(status.HTTP_403_FORBIDDEN)
        return super().write_existing(item_id=0, deps=deps)

    def populate_item(self, _: str = None) -> GroupInDB:
        self.item = self.db.groups.get(self.group_id)
        return self.item

    # ====================================================================
    # Manage Menbers

    def get_members(self) -> list[UserOut]:
        return self.db.users.multi_query(query_by={"group_id": self.item.id}, override_schema=UserOut)

    def set_member_permissions(self, permissions: SetPermissions) -> PrivateUser:
        target_user = self.db.users.get(permissions.user_id)

        if not target_user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

        if target_user.group_id != self.group_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User is not a member of this group")

        target_user.can_invite = permissions.can_invite
        target_user.can_manage = permissions.can_manage
        target_user.can_organize = permissions.can_organize

        return self.db.users.update(permissions.user_id, target_user)

    # ====================================================================
    # Meal Categories

    def update_categories(self, new_categories: list[CategoryBase]):
        self.item.categories = new_categories
        return self.db.groups.update(self.group_id, self.item)

    # ====================================================================
    # Preferences

    def update_preferences(self, new_preferences: UpdateGroupPreferences):
        self.db.group_preferences.update(self.group_id, new_preferences)
        return self.populate_item()

    # ====================================================================
    # Group Invites

    def create_invite_token(self, uses: int = 1) -> None:
        if not self.user.can_invite:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User is not allowed to create invite tokens")

        token = SaveInviteToken(uses_left=uses, group_id=self.group_id, token=uuid4().hex)
        return self.db.group_invite_tokens.create(token)

    def get_invite_tokens(self) -> list[ReadInviteToken]:
        return self.db.group_invite_tokens.multi_query({"group_id": self.group_id})

    def email_invitation(self, invite: EmailInvitation) -> EmailInitationResponse:
        email_service = EmailService()
        url = f"{self.settings.BASE_URL}/register?token={invite.token}"

        success = False
        error = None
        try:
            success = email_service.send_invitation(address=invite.email, invitation_url=url)
        except Exception as e:
            error = str(e)

        return EmailInitationResponse(success=success, error=error)

    # ====================================================================
    # Export / Import Recipes
