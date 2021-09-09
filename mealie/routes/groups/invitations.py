from fastapi import APIRouter, Depends, status

from mealie.schema.group.invite_token import CreateInviteToken, ReadInviteToken
from mealie.services.group_services.group_service import GroupSelfService

router = APIRouter()


@router.get("", response_model=list[ReadInviteToken])
def get_invite_tokens(g_service: GroupSelfService = Depends(GroupSelfService.write_existing)):
    return g_service.get_invite_tokens()


@router.post("", response_model=ReadInviteToken, status_code=status.HTTP_201_CREATED)
def create_invite_token(
    uses: CreateInviteToken, g_service: GroupSelfService = Depends(GroupSelfService.write_existing)
):
    return g_service.create_invite_token(uses.uses)
