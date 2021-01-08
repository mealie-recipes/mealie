from pprint import pprint

from fastapi import APIRouter, HTTPException
from services.meal_services import MealPlan
from utils.snackbar import SnackResponse

router = APIRouter()


@router.get("/api/meal-plan/all/", tags=["Meal Plan"])
async def get_all_meals():
    """ Returns a list of all available meal plans """

    return MealPlan.get_all()


@router.post("/api/meal-plan/create/", tags=["Meal Plan"])
async def set_meal_plan(data: MealPlan):
    """ Creates a mealplan database entry"""
    data.process_meals()
    data.save_to_db()

    #     raise HTTPException(
    #         status_code=404,
    #         detail=SnackResponse.error("Unable to Create Mealplan See Log"),
    #     )

    return SnackResponse.success("Mealplan Created")


@router.post("/api/meal-plan/{plan_id}/update/", tags=["Meal Plan"])
async def update_meal_plan(plan_id: str, meal_plan: MealPlan):
    """ Updates a Meal Plan Based off ID """

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
async def delete_meal_plan(plan_id):
    """ Doc Str """

    MealPlan.delete(plan_id)

    return SnackResponse.success("Mealplan Deleted")


@router.get("/api/meal-plan/today/", tags=["Meal Plan"])
async def get_today():
    """ Returns the meal plan data for today """

    return MealPlan.today()


@router.get("/api/meal-plan/this-week/", tags=["Meal Plan"])
async def get_this_week():
    """ Returns the meal plan data for this week """

    return MealPlan.this_week()
