from fastapi import APIRouter, Depends

from mealie.routes._base import BaseAdminController, controller
from mealie.schema.household.invite_token import (
    ReadInviteToken,
)
from mealie.schema.make_dependable import make_dependable
from mealie.schema.response.pagination import PaginationQuery

router = APIRouter(prefix="/invitations")


@controller(router)
class AdminInvitationsController(BaseAdminController):
    @router.get("", response_model=list[ReadInviteToken])
    def get_all(
        self,
        q: PaginationQuery = Depends(make_dependable(PaginationQuery)),
    ):
        """Get all invite tokens"""
        return self.repos.group_invite_tokens.page_all(pagination=q).items
