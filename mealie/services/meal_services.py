from datetime import date, timedelta
from typing import Union

from mealie.db.database import db
from mealie.db.db_setup import create_session
from mealie.schema.meal import MealDayIn, MealPlanIn
from mealie.schema.recipe import Recipe
from mealie.schema.user import GroupInDB
from sqlalchemy.orm.session import Session


def set_mealplan_dates(meal_plan_base: MealPlanIn) -> MealPlanIn:
    for x, plan_days in enumerate(meal_plan_base.plan_days):
        plan_days: MealDayIn

        plan_days.date = meal_plan_base.start_date + timedelta(days=x)


def get_todays_meal(session: Session, group: Union[int, GroupInDB]) -> Recipe:
    """Returns the given mealplan for today based off the group. If the group
    Type is of type int, then a query will be made to the database to get the
    grop object."

    Args:
        session (Session): SqlAlchemy Session
        group (Union[int, GroupInDB]): Either the id of the group or the GroupInDB Object

    Returns:
        Recipe: Pydantic Recipe Object
    """

    return

    # session = session or create_session()

    # if isinstance(group, int):
    #     group: GroupInDB = db.groups.get(session, group)

    # today_slug = None

    # for mealplan in group.mealplans:
    #     for meal in mealplan.meals:
    #         if meal.date == date.today():
    #             today_slug = meal.slug
    #             break

    # if today_slug:
    #     return db.recipes.get(session, today_slug)
    # else:
    #     return None
