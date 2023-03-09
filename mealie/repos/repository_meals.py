from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.group import GroupMealPlan
from mealie.schema.meal_plan.new_meal import ReadPlanEntry

from ..db.models.recipe import RecipeModel
from .repository_generic import RepositoryGeneric


class RepositoryMeals(RepositoryGeneric[ReadPlanEntry, GroupMealPlan]):
    def by_group(self, group_id: UUID) -> "RepositoryMeals":
        return super().by_group(group_id)

    def get_today(self, group_id: UUID) -> list[ReadPlanEntry]:
        today = date.today()
        stmt = select(GroupMealPlan).filter(GroupMealPlan.date == today, GroupMealPlan.group_id == group_id)
        plans = self.session.execute(stmt).scalars().all()
        return [self.schema.from_orm(x) for x in plans]

    def paging_query_options(self) -> list[LoaderOption]:
        return [
            joinedload(GroupMealPlan.recipe).joinedload(RecipeModel.recipe_category),
            joinedload(GroupMealPlan.recipe).joinedload(RecipeModel.tags),
            joinedload(GroupMealPlan.recipe).joinedload(RecipeModel.tools),
        ]
