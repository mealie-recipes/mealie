from datetime import date, timedelta

from db.database import db
from schema.meal import MealIn, MealOut, MealPlanBase, MealPlanProcessed
from schema.recipe import Recipe
from sqlalchemy.orm.session import Session


def process_meals(session: Session, meal_plan_base: MealPlanBase) -> MealPlanProcessed:
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

        except:

            meal_data = MealOut(
                date=meal_plan_base.startDate + timedelta(days=x),
            )

        meals.append(meal_data)

    return MealPlanProcessed(
        meals=meals, startDate=meal_plan_base.startDate, endDate=meal_plan_base.endDate
    )


def get_todays_meal(session):
    meal_plan = db.meals.get_all(session, limit=1, order_by="startDate")

    for meal in meal_plan:
        meal: MealOut
        if meal.date == date.today():
            return meal.slug
