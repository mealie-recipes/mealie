from uuid import UUID

from fastapi import APIRouter, Depends
from slugify import slugify
from sqlalchemy.orm.session import Session

from mealie.db.db_setup import generate_session
from mealie.repos.all_repositories import get_repositories
from mealie.schema.response import ValidationResponse

router = APIRouter()


@router.get("/user/name", response_model=ValidationResponse)
def validate_user(name: str, session: Session = Depends(generate_session)):
    """Checks if a user with the given name exists"""
    db = get_repositories(session, group_id=None, household_id=None)
    existing_element = db.users.get_one(name, "username", any_case=True)
    return ValidationResponse(valid=existing_element is None)


@router.get("/user/email", response_model=ValidationResponse)
def validate_user_email(email: str, session: Session = Depends(generate_session)):
    """Checks if a user with the given name exists"""
    db = get_repositories(session, group_id=None, household_id=None)
    existing_element = db.users.get_one(email, "email", any_case=True)
    return ValidationResponse(valid=existing_element is None)


@router.get("/group", response_model=ValidationResponse)
def validate_group(name: str, session: Session = Depends(generate_session)):
    """Checks if a group with the given name exists"""
    db = get_repositories(session, group_id=None, household_id=None)
    existing_element = db.groups.get_by_name(name)
    return ValidationResponse(valid=existing_element is None)


@router.get("/household", response_model=ValidationResponse)
def validate_household(name: str, session: Session = Depends(generate_session)):
    """Checks if a household with the given name exists"""
    db = get_repositories(session, group_id=None, household_id=None)
    existing_element = db.households.get_by_name(name)
    return ValidationResponse(valid=existing_element is None)


@router.get("/recipe", response_model=ValidationResponse)
def validate_recipe(group_id: UUID, name: str, session: Session = Depends(generate_session)):
    """Checks if a recipe with the given slug exists"""
    db = get_repositories(session, group_id=None, household_id=None)
    slug = slugify(name)
    existing_element = db.recipes.get_by_slug(group_id, slug)
    return ValidationResponse(valid=existing_element is None)
