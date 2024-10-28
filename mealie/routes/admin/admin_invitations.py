from fastapi import APIRouter

from mealie.routes._base import BaseAdminController, controller
from mealie.schema.household.invite_token import (
    ReadInviteToken,
)
from mealie.schema.response.pagination import PaginationQuery

router = APIRouter(prefix="/invitations")


@controller(router)
class AdminInvitationsController(BaseAdminController):
    @router.get("", response_model=list[ReadInviteToken])
    def get_all(self):
        """Get all invite tokens"""
        self.repos.group_id = None
        self.repos.household_id = None
        return self.repos.group_invite_tokens.page_all(PaginationQuery(page=1, per_page=-1)).items

    @router.get("/{group_slug}", response_model=list[ReadInviteToken])
    def get_one(self, group_slug: str):
        """Get all invite tokens for a specific group"""
        self.repos.group_id = self.repos.groups.get_by_slug_or_id(group_slug).id
        return self.repos.group_invite_tokens.page_all(PaginationQuery(page=1, per_page=-1)).items
