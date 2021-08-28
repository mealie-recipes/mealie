from fastapi import Depends, status

from mealie.db.database import db
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
    return db.ingredient_foods.get_all(session)


@router.post("", response_model=IngredientFood, status_code=status.HTTP_201_CREATED)
async def create_unit(unit: CreateIngredientFood, session: Session = Depends(generate_session)):
    """ Create unit in the Database """

    return db.ingredient_foods.create(session, unit)


@router.get("/{id}")
async def get_unit(id: str, session: Session = Depends(generate_session)):
    """ Get unit from the Database """

    return db.ingredient_foods.get(session, id)


@router.put("/{id}")
async def update_unit(id: str, unit: CreateIngredientFood, session: Session = Depends(generate_session)):
    """ Update unit in the Database """

    return db.ingredient_foods.update(session, id, unit)


@router.delete("/{id}")
async def delete_unit(id: str, session: Session = Depends(generate_session)):
    """ Delete unit from the Database """
    return db.ingredient_foods.delete(session, id)
