from pydantic import UUID4

from mealie.schema._mealie import MealieModel


class SetPermissions(MealieModel):
    user_id: UUID4
    can_manage: bool = False
    can_invite: bool = False
    can_organize: bool = False
