from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status

from mealie.core.security import url_safe_token
from mealie.routes._base import BaseUserController, controller
from mealie.schema.household.invite_token import (
    CreateInviteToken,
    EmailInitationResponse,
    EmailInvitation,
    ReadInviteToken,
    SaveInviteToken,
)
from mealie.schema.response.pagination import PaginationQuery
from mealie.services.email.email_service import EmailService

router = APIRouter(prefix="/households/invitations", tags=["Households: Invitations"])


@controller(router)
class GroupInvitationsController(BaseUserController):
    @router.get("", response_model=list[ReadInviteToken])
    def get_invite_tokens(self):
        return self.repos.group_invite_tokens.page_all(PaginationQuery(page=1, per_page=-1)).items

    @router.post("", response_model=ReadInviteToken, status_code=status.HTTP_201_CREATED)
    def create_invite_token(self, uses: CreateInviteToken):
        if not self.user.can_invite:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="User is not allowed to create invite tokens",
            )

        token = SaveInviteToken(
            uses_left=uses.uses, group_id=self.group_id, household_id=self.household_id, token=url_safe_token()
        )
        return self.repos.group_invite_tokens.create(token)

    @router.post("/email", response_model=EmailInitationResponse)
    def email_invitation(
        self,
        invite: EmailInvitation,
        accept_language: Annotated[str | None, Header()] = None,
    ):
        email_service = EmailService(locale=accept_language)
        url = f"{self.settings.BASE_URL}/register?token={invite.token}"

        success = False
        error = None
        try:
            success = email_service.send_invitation(address=invite.email, invitation_url=url)
        except Exception as e:
            error = str(e)

        return EmailInitationResponse(success=success, error=error)
