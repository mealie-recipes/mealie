from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from mealie.db.db_setup import generate_session
from mealie.repos.all_repositories import get_repositories
from mealie.schema.response import ValidationResponse

router = APIRouter()


@router.get("/user/{name}", response_model=ValidationResponse)
def validate_user(name: str, session: Session = Depends(generate_session)):
    """Checks if a user with the given name exists"""
    db = get_repositories(session)
    existing_element = db.users.get_by_username(name)
    return ValidationResponse(valid=existing_element is None)


@router.get("/group/{name}", response_model=ValidationResponse)
def validate_group(name: str, session: Session = Depends(generate_session)):
    """Checks if a group with the given name exists"""
    db = get_repositories(session)
    existing_element = db.groups.get_by_name(name)
    return ValidationResponse(valid=existing_element is None)


@router.get("/recipe/{group_id}/{slug}", response_model=ValidationResponse)
def validate_recipe(group_id: UUID, slug: str, session: Session = Depends(generate_session)):
    """Checks if a group with the given slug exists"""
    db = get_repositories(session)
    existing_element = db.recipes.get_by_slug(group_id, slug)
    return ValidationResponse(valid=existing_element is None)
