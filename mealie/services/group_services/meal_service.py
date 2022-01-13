from __future__ import annotations

from datetime import date
from functools import cached_property

from mealie.schema.meal_plan import CreatePlanEntry, ReadPlanEntry, SavePlanEntry, UpdatePlanEntry

from .._base_http_service.crud_http_mixins import CrudHttpMixins
from .._base_http_service.http_services import UserHttpService
from ..events import create_group_event


class MealService(CrudHttpMixins[CreatePlanEntry, ReadPlanEntry, UpdatePlanEntry], UserHttpService[int, ReadPlanEntry]):
    event_func = create_group_event
    _restrict_by_group = True

    _schema = ReadPlanEntry
    item: ReadPlanEntry

    @cached_property
    def repo(self):
        return self.db.meals

    def populate_item(self, id: int) -> ReadPlanEntry:
        self.item = self.repo.get_one(id)
        return self.item

    def get_slice(self, start: date = None, end: date = None) -> list[ReadPlanEntry]:
        # 2 days ago
        return self.repo.get_slice(start, end, group_id=self.group_id)

    def get_today(self) -> list[ReadPlanEntry]:
        return self.repo.get_today(group_id=self.group_id)

    def create_one(self, data: CreatePlanEntry) -> ReadPlanEntry:
        data = self.cast(data, SavePlanEntry)
        return self._create_one(data)

    def update_one(self, data: UpdatePlanEntry, id: int = None) -> ReadPlanEntry:
        target_id = id or self.item.id
        return self._update_one(data, target_id)

    def delete_one(self, id: int = None) -> ReadPlanEntry:
        target_id = id or self.item.id
        return self._delete_one(target_id)
