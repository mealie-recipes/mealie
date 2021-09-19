from fastapi import Depends, status

from mealie.db.database import get_database
from mealie.db.db_setup import Session, generate_session
from mealie.routes.routers import UserAPIRouter
from mealie.schema.recipe import CreateIngredientFood, IngredientFood

router = UserAPIRouter()


@router.get("", response_model=list[IngredientFood])
async def get_all(
    session: Session = Depends(generate_session),
):
    """ Get unit from the Database """
    # Get unit
    db = get_database(session)
    return db.ingredient_foods.get_all()


@router.post("", response_model=IngredientFood, status_code=status.HTTP_201_CREATED)
async def create_food(unit: CreateIngredientFood, session: Session = Depends(generate_session)):
    """ Create unit in the Database """
    db = get_database(session)
    return db.ingredient_foods.create(unit)


@router.get("/{id}")
async def get_food(id: str, session: Session = Depends(generate_session)):
    """ Get unit from the Database """
    db = get_database(session)
    return db.ingredient_foods.get(id)


@router.put("/{id}")
async def update_food(id: str, unit: CreateIngredientFood, session: Session = Depends(generate_session)):
    """ Update unit in the Database """
    db = get_database(session)
    return db.ingredient_foods.update(id, unit)


@router.delete("/{id}")
async def delete_food(id: str, session: Session = Depends(generate_session)):
    """ Delete unit from the Database """
    db = get_database(session)
    return db.ingredient_foods.delete(id)
