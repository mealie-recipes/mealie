from typing import List

from db.database import db
from db.db_setup import generate_session
from fastapi import APIRouter, Depends, HTTPException
from schema.snackbar import SnackResponse
from services.meal_services import MealPlan
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/meal-plans", tags=["Meal Plan"])


@router.get("/all", response_model=List[MealPlan])
def get_all_meals(session: Session = Depends(generate_session)):
    """ Returns a list of all available Meal Plan """

    return MealPlan.get_all(session)


@router.get("/{id}/shopping-list")
def get_shopping_list(id: str, session: Session = Depends(generate_session)):

    #! Refactor into Single Database Call
    mealplan = db.meals.get(session, id)
    slugs = [x.get("slug") for x in mealplan.get("meals")]
    recipes = [db.recipes.get(session, x) for x in slugs]
    ingredients = [
        {"name": x.get("name"), "recipeIngredient": x.get("recipeIngredient")}
        for x in recipes
        if x
    ]

    return ingredients


@router.post("/create")
def set_meal_plan(data: MealPlan, session: Session = Depends(generate_session)):
    """ Creates a meal plan database entry """
    data.process_meals(session)
    data.save_to_db(session)

    return SnackResponse.success("Mealplan Created")


@router.get("/this-week", response_model=MealPlan)
def get_this_week(session: Session = Depends(generate_session)):
    """ Returns the meal plan data for this week """

    return MealPlan.this_week(session)


@router.put("/{plan_id}")
def update_meal_plan(
    plan_id: str, meal_plan: MealPlan, session: Session = Depends(generate_session)
):
    """ Updates a meal plan based off ID """
    meal_plan.process_meals(session)
    meal_plan.update(session, plan_id)

    return SnackResponse.info("Mealplan Updated")


@router.delete("/{plan_id}")
def delete_meal_plan(plan_id, session: Session = Depends(generate_session)):
    """ Removes a meal plan from the database """

    MealPlan.delete(session, plan_id)

    return SnackResponse.error("Mealplan Deleted")


@router.get("/today", tags=["Meal Plan"])
def get_today(session: Session = Depends(generate_session)):
    """
    Returns the recipe slug for the meal scheduled for today.
    If no meal is scheduled nothing is returned
    """

    return MealPlan.today(session)
