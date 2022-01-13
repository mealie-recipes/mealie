from fastapi import APIRouter, HTTPException, status

from mealie.core.security import url_safe_token
from mealie.routes._base import BaseUserController, controller
from mealie.schema.group.invite_token import (
    CreateInviteToken,
    EmailInitationResponse,
    EmailInvitation,
    ReadInviteToken,
    SaveInviteToken,
)
from mealie.services.email.email_service import EmailService

router = APIRouter(prefix="/groups/invitations", tags=["Groups: Invitations"])


@controller(router)
class GroupInvitationsController(BaseUserController):
    @router.get("", response_model=list[ReadInviteToken])
    def get_invite_tokens(self):
        return self.repos.group_invite_tokens.multi_query({"group_id": self.group_id})

    @router.post("", response_model=ReadInviteToken, status_code=status.HTTP_201_CREATED)
    def create_invite_token(self, uses: CreateInviteToken):
        if not self.deps.acting_user.can_invite:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User is not allowed to create invite tokens")

        token = SaveInviteToken(uses_left=uses.uses, group_id=self.group_id, token=url_safe_token())
        return self.repos.group_invite_tokens.create(token)

    @router.post("/email", response_model=EmailInitationResponse)
    def email_invitation(self, invite: EmailInvitation):
        email_service = EmailService()
        url = f"{self.deps.settings.BASE_URL}/register?token={invite.token}"

        success = False
        error = None
        try:
            success = email_service.send_invitation(address=invite.email, invitation_url=url)
        except Exception as e:
            error = str(e)

        return EmailInitationResponse(success=success, error=error)
