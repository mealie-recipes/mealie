from datetime import date, timedelta
from typing import Union

from mealie.db.database import db
from mealie.db.db_setup import create_session
from mealie.schema.meal import MealIn, MealOut, MealPlanIn, MealPlanInDB, MealPlanProcessed
from mealie.schema.recipe import Recipe
from mealie.schema.user import GroupInDB
from sqlalchemy.orm.session import Session


def process_meals(session: Session, meal_plan_base: MealPlanIn) -> MealPlanProcessed:
    meals = []
    for x, meal in enumerate(meal_plan_base.meals):
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

        except Exception:

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
    session = session or create_session()

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
