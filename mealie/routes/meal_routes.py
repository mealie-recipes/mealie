from typing import List

from fastapi import APIRouter, HTTPException
from models.recipe_models import SlugResponse
from services.meal_services import MealPlan
from utils.snackbar import SnackResponse

router = APIRouter()


@router.get("/api/meal-plan/all/", tags=["Meal Plan"], response_model=List[MealPlan])
def get_all_meals():
    """ Returns a list of all available Meal Plan """

    return MealPlan.get_all()


@router.post("/api/meal-plan/create/", tags=["Meal Plan"])
def set_meal_plan(data: MealPlan):
    """ Creates a meal plan database entry """
    data.process_meals()
    data.save_to_db()

    #     raise HTTPException(
    #         status_code=404,
    #         detail=SnackResponse.error("Unable to Create Mealplan See Log"),
    #     )

    return SnackResponse.success("Mealplan Created")


@router.post("/api/meal-plan/{plan_id}/update/", tags=["Meal Plan"])
def update_meal_plan(plan_id: str, meal_plan: MealPlan):
    """ Updates a meal plan based off ID """

    try:
        meal_plan.process_meals()
        meal_plan.update(plan_id)
    except:
        raise HTTPException(
            status_code=404,
            detail=SnackResponse.error("Unable to Update Mealplan"),
        )

    return SnackResponse.success("Mealplan Updated")


@router.delete("/api/meal-plan/{plan_id}/delete/", tags=["Meal Plan"])
def delete_meal_plan(plan_id):
    """ Removes a meal plan from the database """

    MealPlan.delete(plan_id)

    return SnackResponse.success("Mealplan Deleted")


@router.get(
    "/api/meal-plan/today/",
    tags=["Meal Plan"],
)
def get_today():
    """
    Returns the recipe slug for the meal scheduled for today.
    If no meal is scheduled nothing is returned
    """

    return MealPlan.today()


@router.get("/api/meal-plan/this-week/", tags=["Meal Plan"], response_model=MealPlan)
def get_this_week():
    """ Returns the meal plan data for this week """

    return MealPlan.this_week()
