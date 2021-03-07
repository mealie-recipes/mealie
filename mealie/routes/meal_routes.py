from datetime import date
from typing import List

from db.database import db
from db.db_setup import generate_session
from fastapi import APIRouter, Depends
from schema.meal import MealPlanBase, MealPlanInDB
from schema.snackbar import SnackResponse
from services.meal_services import get_todays_meal, process_meals
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/meal-plans", tags=["Meal Plan"])


@router.get("/all", response_model=List[MealPlanInDB])
def get_all_meals(session: Session = Depends(generate_session)):
    """ Returns a list of all available Meal Plan """

    return db.meals.get_all(session)


@router.get("/{id}/shopping-list")
def get_shopping_list(id: str, session: Session = Depends(generate_session)):

    #! Refactor into Single Database Call
    mealplan = db.meals.get(session, id)
    mealplan: MealPlanInDB
    slugs = [x.slug for x in mealplan.meals]
    recipes = [db.recipes.get(session, x) for x in slugs]
    ingredients = [
        {"name": x.get("name"), "recipeIngredient": x.get("recipeIngredient")}
        for x in recipes
        if x
    ]

    return ingredients


@router.post("/create")
def create_meal_plan(data: MealPlanBase, session: Session = Depends(generate_session)):
    """ Creates a meal plan database entry """
    processed_plan = process_meals(session, data)
    db.meals.create(session, processed_plan.dict())

    return SnackResponse.success("Mealplan Created")


@router.get("/this-week", response_model=MealPlanInDB)
def get_this_week(session: Session = Depends(generate_session)):
    """ Returns the meal plan data for this week """

    return db.meals.get_all(session, limit=1, order_by="startDate")


@router.put("/{plan_id}")
def update_meal_plan(
    plan_id: str, meal_plan: MealPlanBase, session: Session = Depends(generate_session)
):
    """ Updates a meal plan based off ID """
    processed_plan = process_meals(session, meal_plan)
    processed_plan = MealPlanInDB(uid=plan_id, **processed_plan.dict())
    db.meals.update(session, plan_id, processed_plan.dict())

    return SnackResponse.info("Mealplan Updated")


@router.delete("/{plan_id}")
def delete_meal_plan(plan_id, session: Session = Depends(generate_session)):
    """ Removes a meal plan from the database """

    db.meals.delete(session, plan_id)

    return SnackResponse.error("Mealplan Deleted")


@router.get("/today", tags=["Meal Plan"])
def get_today(session: Session = Depends(generate_session)):
    """
    Returns the recipe slug for the meal scheduled for today.
    If no meal is scheduled nothing is returned
    """

    return get_todays_meal(session)
