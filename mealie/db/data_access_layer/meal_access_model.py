from datetime import date

from sqlalchemy.orm.session import Session

from mealie.db.models.group import GroupMealPlan
from mealie.schema.meal_plan.new_meal import ReadPlanEntry

from ._base_access_model import BaseAccessModel


class MealDataAccessModel(BaseAccessModel[ReadPlanEntry, GroupMealPlan]):
    def get_slice(self, session: Session, start: date, end: date, group_id: int) -> list[ReadPlanEntry]:
        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")
        qry = session.query(GroupMealPlan).filter(
            GroupMealPlan.date.between(start, end),
            GroupMealPlan.group_id == group_id,
        )

        return [self.schema.from_orm(x) for x in qry.all()]

    def get_today(self, session: Session, group_id: int) -> list[ReadPlanEntry]:
        today = date.today()
        qry = session.query(GroupMealPlan).filter(GroupMealPlan.date == today, GroupMealPlan.group_id == group_id)

        return [self.schema.from_orm(x) for x in qry.all()]
