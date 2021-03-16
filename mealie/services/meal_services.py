from datetime import date, timedelta, timezone
from typing import Union

import pytz
from db.database import db
from db.db_setup import create_session
from pydantic.tools import T
from schema.meal import MealIn, MealOut, MealPlanIn, MealPlanInDB, MealPlanProcessed
from schema.recipe import Recipe
from schema.user import GroupInDB
from sqlalchemy.orm.session import Session


def process_meals(session: Session, meal_plan_base: MealPlanIn) -> MealPlanProcessed:
    meals = []
    for x, meal in enumerate(meal_plan_base.meals):
        # europe = pytz.timezone("America/Anchorage")
        # d = europe.localize(meal_plan_base.startDate)
        # print(d)

        meal: MealIn
        try:
            recipe: Recipe = db.recipes.get(session, meal.slug)

            meal_data = MealOut(
                slug=recipe.slug,
                name=recipe.name,
                date=meal_plan_base.startDate + timedelta(days=x),
                image=recipe.image,
                description=recipe.description,
            )

        except:

            meal_data = MealOut(
                date=meal_plan_base.startDate + timedelta(days=x),
            )

        meals.append(meal_data)

    return MealPlanProcessed(
        group=meal_plan_base.group,
        meals=meals,
        startDate=meal_plan_base.startDate,
        endDate=meal_plan_base.endDate,
    )


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
    session = session if session else create_session()

    if isinstance(group, int):
        group: GroupInDB = db.groups.get(session, group)

    today_slug = None

    for mealplan in group.mealplans:
        mealplan: MealPlanInDB
        for meal in mealplan.meals:
            meal: MealOut
            if meal.date == date.today():
                today_slug = meal.slug
                break

    if today_slug:
        return db.recipes.get(session, today_slug)
    else:
        return None
