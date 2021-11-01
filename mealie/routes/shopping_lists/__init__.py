from fastapi import Depends
from sqlalchemy.orm.session import Session

from mealie.core.dependencies import get_current_user
from mealie.db.database import get_database
from mealie.db.db_setup import generate_session
from mealie.routes.routers import UserAPIRouter
from mealie.schema.meal_plan import ShoppingList
from mealie.schema.user import PrivateUser

import os

router = UserAPIRouter(prefix="/shopping-lists", tags=["Shopping Lists: CRUD"])


@router.post("", response_model=ShoppingList)
async def create_shopping_list(
    list_in: ShoppingList,
    current_user: PrivateUser = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """Create Shopping List in the Database"""
    db = get_database(session)
    list_in.group = current_user.group

    return db.shopping_lists.create(list_in)


@router.get("", response_model=ShoppingList)
async def get_shopping_lists(
    current_user: PrivateUser = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    """Get All Shopping Lists in the user's group"""
    db = get_database(session)

    # TODO--group-ify this with current_user.group

    return db.shopping_lists.get_all()


@router.get("/{id}", response_model=ShoppingList)
async def get_shopping_list(id: int, session: Session = Depends(generate_session)):
    """Get Shopping List from the Database"""
    db = get_database(session)
    return db.shopping_lists.get(id)


@router.put("/{id}", response_model=ShoppingList)
async def update_shopping_list(id: int, new_data: ShoppingList, session: Session = Depends(generate_session)):
    """Update Shopping List in the Database"""
    db = get_database(session)
    return db.shopping_lists.update(id, new_data)


@router.delete("/{id}")
async def delete_shopping_list(id: int, session: Session = Depends(generate_session)):
    """Delete Shopping List from the Database"""
    db = get_database(session)
    return db.shopping_lists.delete(id)
