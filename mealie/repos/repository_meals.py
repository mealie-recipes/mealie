from datetime import date
from math import ceil
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.sql import sqltypes

from mealie.db.models.group import GroupMealPlan
from mealie.schema.meal_plan.new_meal import PlanEntryPagination, ReadPlanEntry
from mealie.schema.response.pagination import OrderDirection, PaginationQuery

from .repository_generic import RepositoryGeneric


class RepositoryMeals(RepositoryGeneric[ReadPlanEntry, GroupMealPlan]):
    def by_group(self, group_id: UUID) -> "RepositoryMeals":
        return super().by_group(group_id)  # type: ignore

    def get_slice(
        self, pagination: PaginationQuery, start_date: date, end_date: date, group_id: UUID
    ) -> PlanEntryPagination:
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        # get the total number of documents
        q = self.session.query(GroupMealPlan).filter(
            GroupMealPlan.date.between(start_str, end_str),
            GroupMealPlan.group_id == group_id,
        )

        count = q.count()

        # interpret -1 as "get_all"
        if pagination.per_page == -1:
            pagination.per_page = count

        try:
            total_pages = ceil(count / pagination.per_page)

        except ZeroDivisionError:
            total_pages = 0

        # interpret -1 as "last page"
        if pagination.page == -1:
            pagination.page = total_pages

        # failsafe for user input error
        if pagination.page < 1:
            pagination.page = 1

        if pagination.order_by:
            if order_attr := getattr(self.model, pagination.order_by, None):
                # queries handle uppercase and lowercase differently, which is undesirable
                if isinstance(order_attr.type, sqltypes.String):
                    order_attr = func.lower(order_attr)

                if pagination.order_direction == OrderDirection.asc:
                    order_attr = order_attr.asc()
                elif pagination.order_direction == OrderDirection.desc:
                    order_attr = order_attr.desc()

                q = q.order_by(order_attr)

        q = q.limit(pagination.per_page).offset((pagination.page - 1) * pagination.per_page)

        try:
            data = [self.schema.from_orm(x) for x in q.all()]
        except Exception as e:
            self._log_exception(e)
            self.session.rollback()
            raise e

        return PlanEntryPagination(
            page=pagination.page,
            per_page=pagination.per_page,
            total=count,
            total_pages=total_pages,
            items=data,
        )

    def get_today(self, group_id: UUID) -> list[ReadPlanEntry]:
        today = date.today()
        qry = self.session.query(GroupMealPlan).filter(GroupMealPlan.date == today, GroupMealPlan.group_id == group_id)

        return [self.schema.from_orm(x) for x in qry.all()]
