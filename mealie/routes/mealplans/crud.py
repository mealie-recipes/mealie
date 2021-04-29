from fastapi import APIRouter, Depends, HTTPException, status
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.schema.meal import MealPlanIn, MealPlanInDB
from mealie.schema.user import GroupInDB, UserInDB
from mealie.services.image import image
from mealie.services.meal_services import get_todays_meal, process_meals
from sqlalchemy.orm.session import Session
from starlette.responses import FileResponse

router = APIRouter(prefix="/api/meal-plans", tags=["Meal Plan"])


@router.get("/all", response_model=list[MealPlanInDB])
def get_all_meals(
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """ Returns a list of all available Meal Plan """

    return db.groups.get_meals(session, current_user.group)


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_meal_plan(
    data: MealPlanIn, session: Session = Depends(generate_session), current_user=Depends(get_current_user)
):
    """ Creates a meal plan database entry """
    processed_plan = process_meals(session, data)
    return db.meals.create(session, processed_plan.dict())


@router.put("/{plan_id}")
def update_meal_plan(
    plan_id: str,
    meal_plan: MealPlanIn,
    session: Session = Depends(generate_session),
    current_user=Depends(get_current_user),
):
    """ Updates a meal plan based off ID """
    processed_plan = process_meals(session, meal_plan)
    processed_plan = MealPlanInDB(uid=plan_id, **processed_plan.dict())
    try:
        db.meals.update(session, plan_id, processed_plan.dict())
    except:
        raise HTTPException( status.HTTP_400_BAD_REQUEST )


@router.delete("/{plan_id}")
def delete_meal_plan(plan_id, session: Session = Depends(generate_session), current_user=Depends(get_current_user)):
    """ Removes a meal plan from the database """

    try:
        db.meals.delete(session, plan_id)
    except:
        raise HTTPException( status.HTTP_400_BAD_REQUEST )


@router.get("/this-week", response_model=MealPlanInDB)
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
        return recipe.slug


@router.get("/today/image", tags=["Meal Plan"])
def get_todays_image(session: Session = Depends(generate_session), group_name: str = "Home"):
    """
    Returns the image for todays meal-plan.
    """

    group_in_db: GroupInDB = db.groups.get(session, group_name, "name")
    recipe = get_todays_meal(session, group_in_db)

    if recipe:
        recipe_image = image.read_image(recipe.slug, image_type=image.IMG_OPTIONS.ORIGINAL_IMAGE)
    else:
        raise HTTPException( status.HTTP_404_NOT_FOUND )
    if recipe_image:
        return FileResponse(recipe_image)
    else:
        raise HTTPException( status.HTTP_404_NOT_FOUND )
