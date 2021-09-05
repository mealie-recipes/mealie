from __future__ import annotations

from fastapi import Depends, HTTPException, status

from mealie.core.dependencies.grouped import UserDeps
from mealie.core.root_logger import get_logger
from mealie.schema.recipe.recipe_category import CategoryBase
from mealie.schema.user.user import GroupInDB
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_group_event

logger = get_logger(module=__name__)


class GroupSelfService(UserHttpService[int, str]):
    _restrict_by_group = True
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

    def assert_existing(self, _: str = None):
        self.populate_item()

        if not self.item:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        if self.item.id != self.group_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

    def populate_item(self, _: str = None) -> GroupInDB:
        self.item = self.db.groups.get(self.session, self.group_id)
        return self.item

    def update_categories(self, new_categories: list[CategoryBase]):
        if not self.item:
            return
        self.item.categories = new_categories

        return self.db.groups.update(self.session, self.group_id, self.item)
