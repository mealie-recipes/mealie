from __future__ import annotations

from uuid import uuid4

from fastapi import Depends

from mealie.core.dependencies.grouped import UserDeps
from mealie.core.root_logger import get_logger
from mealie.schema.group.group_preferences import UpdateGroupPreferences
from mealie.schema.group.invite_token import ReadInviteToken, SaveInviteToken
from mealie.schema.recipe.recipe_category import CategoryBase
from mealie.schema.user.user import GroupInDB
from mealie.services._base_http_service.http_services import UserHttpService
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

    def populate_item(self, _: str = None) -> GroupInDB:
        self.item = self.db.groups.get(self.group_id)
        return self.item

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
        token = SaveInviteToken(uses_left=uses, group_id=self.group_id, token=uuid4().hex)
        return self.db.group_invite_tokens.create(token)

    def get_invite_tokens(self) -> list[ReadInviteToken]:
        return self.db.group_invite_tokens.multi_query({"group_id": self.group_id})

    # ====================================================================
    # Export / Import Recipes
