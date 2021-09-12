from __future__ import annotations

from datetime import date

from mealie.core.root_logger import get_logger
from mealie.db.database import get_database
from mealie.schema.meal_plan import CreatePlanEntry, ReadPlanEntry, SavePlanEntry, UpdatePlanEntry

from .._base_http_service.crud_http_mixins import CrudHttpMixins
from .._base_http_service.http_services import UserHttpService
from ..events import create_group_event

logger = get_logger(module=__name__)


class MealService(UserHttpService[int, ReadPlanEntry], CrudHttpMixins[CreatePlanEntry, ReadPlanEntry, UpdatePlanEntry]):
    event_func = create_group_event
    _restrict_by_group = True

    _schema = ReadPlanEntry

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dal = get_database().meals

    def populate_item(self, id: int) -> ReadPlanEntry:
        self.item = self.db.meals.get_one(self.session, id)
        return self.item

    def get_slice(self, start: date = None, end: date = None) -> list[ReadPlanEntry]:
        # 2 days ago
        return self.db.meals.get_slice(self.session, start, end, group_id=self.group_id)

    def get_today(self) -> list[ReadPlanEntry]:
        return self.db.meals.get_today(self.session, group_id=self.group_id)

    def create_one(self, data: CreatePlanEntry) -> ReadPlanEntry:
        data = self.cast(data, SavePlanEntry)
        return self._create_one(data)

    def update_one(self, data: UpdatePlanEntry, id: int = None) -> ReadPlanEntry:
        target_id = id or self.item.id
        return self._update_one(data, target_id)

    def delete_one(self, id: int = None) -> ReadPlanEntry:
        target_id = id or self.item.id
        return self._delete_one(target_id)
