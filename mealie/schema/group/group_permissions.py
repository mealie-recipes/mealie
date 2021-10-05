from fastapi_camelcase import CamelModel


class SetPermissions(CamelModel):
    user_id: int
    can_manage: bool = False
    can_invite: bool = False
    can_organize: bool = False
