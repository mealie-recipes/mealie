from uuid import UUID

from fastapi import APIRouter, Depends
from slugify import slugify
from sqlalchemy.orm.session import Session

from mealie.core.dependencies import try_get_current_user
from mealie.db.db_setup import generate_session
from mealie.repos.all_repositories import get_repositories
from mealie.schema.response import ValidationResponse
from mealie.schema.user.user import PrivateUser

router = APIRouter()


@router.get("/user/name", response_model=ValidationResponse)
def validate_user(
    name: str,
    session: Session = Depends(generate_session),
    current_user: PrivateUser | None = Depends(try_get_current_user),
):
    """Checks if a user with the given name exists. The signed-in user's own name is valid."""
    db = get_repositories(session, group_id=None, household_id=None)
    existing_element = db.users.get_one(name, "username", any_case=True)
    return ValidationResponse(valid=existing_element is None or _is_current_user(existing_element.id, current_user))


@router.get("/user/email", response_model=ValidationResponse)
def validate_user_email(
    email: str,
    session: Session = Depends(generate_session),
    current_user: PrivateUser | None = Depends(try_get_current_user),
):
    """Checks if a user with the given email exists. The signed-in user's own email is valid."""
    db = get_repositories(session, group_id=None, household_id=None)
    existing_element = db.users.get_one(email, "email", any_case=True)
    return ValidationResponse(valid=existing_element is None or _is_current_user(existing_element.id, current_user))


def _is_current_user(user_id: UUID, current_user: PrivateUser | None) -> bool:
    # A user who already has an account (e.g. created on first OIDC login) re-submits their own
    # name and email in the setup wizard, which shouldn't count as taken.
    return current_user is not None and current_user.id == user_id


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
