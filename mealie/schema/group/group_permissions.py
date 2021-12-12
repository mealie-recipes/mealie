from fastapi_camelcase import CamelModel
from pydantic import UUID4


class SetPermissions(CamelModel):
    user_id: UUID4
    can_manage: bool = False
    can_invite: bool = False
    can_organize: bool = False
