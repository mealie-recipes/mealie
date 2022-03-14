from fastapi import APIRouter, Depends
from typing import Union
from sqlalchemy.orm.session import Session

from mealie.db.db_setup import generate_session
from mealie.repos.all_repositories import get_repositories
from mealie.schema.user import UserBase
from mealie.schema.response import ErrorResponse, SuccessResponse
from mealie.db.models.users import User
from mealie.db.models.group import Group
from mealie.db.models.recipe.recipe import RecipeModel


router = APIRouter()


def create_response(value, type: str):
    if value is None:
        return SuccessResponse.respond(message=f"No {type} exists")
    return ErrorResponse.respond(message=f"{type.capitalize()} already exists")


@router.get("/user/{name}", response_model=Union[ErrorResponse, SuccessResponse])
async def validate_user(name: str, session: Session = Depends(generate_session)):
    """Checks if a user with the given name exists"""
    db = get_repositories(session)
    existing_element = db.users.get_by_username(name)
    print(existing_element)
    return create_response(existing_element, "user")


@router.get("/group/{name}", response_model=Union[ErrorResponse, SuccessResponse])
async def validate_group(name: str, session: Session = Depends(generate_session)):
    """Checks if a group with the given name exists"""
    db = get_repositories(session)
    existing_element = db.groups.get_by_name(name)
    return create_response(existing_element, "group")


@router.get("/recipe/{name}", response_model=Union[ErrorResponse, SuccessResponse])
async def validate_recipe(name: str, session: Session = Depends(generate_session)):
    """Checks if a group with the given slug exists"""
    db = get_repositories(session)
    existing_element = db.recipes.get_by_slug(name)
    return create_response(existing_element, "recipe")
