from __future__ import annotations

from fastapi import HTTPException, status

from mealie.core.root_logger import get_logger
from mealie.schema.meal_plan.new_meal import CreatePlanEntry, ReadPlanEntry, SavePlanEntry, UpdatePlanEntry
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_group_event

logger = get_logger(module=__name__)


class MealService(UserHttpService[int, ReadPlanEntry]):
    event_func = create_group_event
    _restrict_by_group = True

    _schema = ReadPlanEntry

    def populate_item(self, id: int) -> ReadPlanEntry:
        self.item = self.db.meals.get_one(self.session, id)
        return self.item

    def get_all(self) -> list[ReadPlanEntry]:
        return self.db.meals.get(self.session, self.group_id, match_key="group_id", limit=9999)

    def create_one(self, data: CreatePlanEntry) -> ReadPlanEntry:
        try:
            self.item = self.db.meals.create(self.session, SavePlanEntry(group_id=self.group_id, **data.dict()))
        except Exception as ex:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail={"message": "mealplan-creation-error", "exception": str(ex)}
            )

        return self.item

    def update_one(self, data: UpdatePlanEntry, id: int = None) -> ReadPlanEntry:
        if not self.item:
            return

        target_id = id or self.item.id
        self.item = self.db.meals.update(self.session, target_id, data)

        return self.item

    def delete_one(self, id: int = None) -> ReadPlanEntry:
        if not self.item:
            return

        target_id = id or self.item.id
        self.db.meals.delete(self.session, target_id)

        return self.item
