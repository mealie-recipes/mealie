from typing import List

from db.db_setup import generate_session
from fastapi import APIRouter, Depends, HTTPException
from services.meal_services import MealPlan
from sqlalchemy.orm.session import Session
from utils.snackbar import SnackResponse

router = APIRouter(prefix="/api/meal-plans", tags=["Meal Plan"])


@router.get("/all", response_model=List[MealPlan])
def get_all_meals(db: Session = Depends(generate_session)):
    """ Returns a list of all available Meal Plan """

    return MealPlan.get_all(db)


@router.post("/create")
def set_meal_plan(data: MealPlan, db: Session = Depends(generate_session)):
    """ Creates a meal plan database entry """
    data.process_meals(db)
    data.save_to_db(db)

    return SnackResponse.success("Mealplan Created")


@router.get("/this-week", response_model=MealPlan)
def get_this_week(db: Session = Depends(generate_session)):
    """ Returns the meal plan data for this week """

    return MealPlan.this_week(db)


@router.put("/{plan_id}")
def update_meal_plan(
    plan_id: str, meal_plan: MealPlan, db: Session = Depends(generate_session)
):
    """ Updates a meal plan based off ID """
    meal_plan.process_meals(db)
    meal_plan.update(db, plan_id)

    return SnackResponse.info("Mealplan Updated")


@router.delete("/{plan_id}")
def delete_meal_plan(plan_id, db: Session = Depends(generate_session)):
    """ Removes a meal plan from the database """

    MealPlan.delete(db, plan_id)

    return SnackResponse.error("Mealplan Deleted")


@router.get("/today", tags=["Meal Plan"])
def get_today(db: Session = Depends(generate_session)):
    """
    Returns the recipe slug for the meal scheduled for today.
    If no meal is scheduled nothing is returned
    """

    return MealPlan.today(db)
