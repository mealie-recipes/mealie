from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm.session import Session
from starlette.responses import FileResponse

from mealie.core.dependencies import get_current_user
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.routers import UserAPIRouter
from mealie.schema.meal_plan import MealPlanIn, MealPlanOut
from mealie.schema.user import GroupInDB, UserInDB
from mealie.services.events import create_group_event
from mealie.services.image import image
from mealie.services.meal_services import get_todays_meal, set_mealplan_dates

router = UserAPIRouter(prefix="/api/meal-plans", tags=["Meal Plan"])
public_router = APIRouter(prefix="/api/meal-plans", tags=["Meal Plan"])


@router.get("/all", response_model=list[MealPlanOut])
def get_all_meals(
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Returns a list of all available Meal Plan """

    return db.groups.get_meals(session, current_user.group)


@router.get("/this-week", response_model=MealPlanOut)
def get_this_week(session: Session = Depends(generate_session), current_user: UserInDB = Depends(get_current_user)):
    """ Returns the meal plan data for this week """
    plans = db.groups.get_meals(session, current_user.group)
    if plans:
        return plans[0]


@router.get("/today", tags=["Meal Plan"])
def get_today(session: Session = Depends(generate_session), current_user: UserInDB = Depends(get_current_user)):
    """
    Returns the recipe slug for the meal scheduled for today.
    If no meal is scheduled nothing is returned
    """

    group_in_db: GroupInDB = db.groups.get(session, current_user.group, "name")
    recipe = get_todays_meal(session, group_in_db)
    if recipe:
        return recipe


@public_router.get("/today/image", tags=["Meal Plan"])
def get_todays_image(session: Session = Depends(generate_session), group_name: str = "Home"):
    """
    Returns the image for todays meal-plan.
    """

    group_in_db: GroupInDB = db.groups.get(session, group_name, "name")
    recipe = get_todays_meal(session, group_in_db)
    recipe_image = recipe.image_dir.joinpath(image.ImageOptions.ORIGINAL_IMAGE)

    if not recipe and not recipe_image.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return FileResponse(recipe_image)


@router.get("/{id}", response_model=MealPlanOut)
def get_meal_plan(
    id,
    session: Session = Depends(generate_session),
):
    """ Returns a single Meal Plan from the Database """

    return db.meals.get(session, id)


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_meal_plan(
    background_tasks: BackgroundTasks,
    data: MealPlanIn,
    session: Session = Depends(generate_session),
    current_user: UserInDB = Depends(get_current_user),
):
    """ Creates a meal plan database entry """
    set_mealplan_dates(data)
    background_tasks.add_task(
        create_group_event, "Meal Plan Created", f"Mealplan Created for '{current_user.group}'", session=session
    )
    return db.meals.create(session, data.dict())


@router.put("/{plan_id}")
def update_meal_plan(
    background_tasks: BackgroundTasks,
    plan_id: str,
    meal_plan: MealPlanIn,
    session: Session = Depends(generate_session),
    current_user: UserInDB = Depends(get_current_user),
):
    """ Updates a meal plan based off ID """
    set_mealplan_dates(meal_plan)
    processed_plan = MealPlanOut(id=plan_id, **meal_plan.dict())
    try:
        db.meals.update(session, plan_id, processed_plan.dict())
        background_tasks.add_task(
            create_group_event, "Meal Plan Updated", f"Mealplan Updated for '{current_user.group}'", session=session
        )
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)


@router.delete("/{plan_id}")
def delete_meal_plan(
    background_tasks: BackgroundTasks,
    plan_id,
    session: Session = Depends(generate_session),
    current_user: UserInDB = Depends(get_current_user),
):
    """ Removes a meal plan from the database """

    try:
        db.meals.delete(session, plan_id)
        background_tasks.add_task(
            create_group_event, "Meal Plan Deleted", f"Mealplan Deleted for '{current_user.group}'", session=session
        )
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
