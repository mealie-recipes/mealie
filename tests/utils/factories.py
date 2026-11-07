import random
import string
from typing import Any
from uuid import uuid4

from mealie.schema.recipe.recipe import RecipeOut, create_recipe_slug
from mealie.schema.user.registration import UserRegistrationCreate


def random_string(length=10) -> str:
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length)).strip()


def random_email(length=10) -> str:
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length)) + "@fake.com"


def random_bool() -> bool:
    return bool(random.getrandbits(1))


def random_int(min=-4294967296, max=4294967296) -> int:
    return random.randint(min, max)


def user_registration_factory(advanced=None, private=None) -> UserRegistrationCreate:
    return UserRegistrationCreate(
        group=random_string(),
        household=random_string(),
        email=random_email(),
        username=random_string(),
        full_name=random_string(),
        password="fake-password",
        password_confirm="fake-password",
        advanced=advanced or random_bool(),
        private=private or random_bool(),
    )


def build_recipe(**fields: Any) -> RecipeOut:
    """A saved recipe built in memory, for tests that render one without the database."""
    name = fields.pop("name", None) or random_string()
    return RecipeOut.model_validate(
        {
            "id": uuid4(),
            "user_id": uuid4(),
            "household_id": uuid4(),
            "group_id": uuid4(),
            "name": name,
            "slug": create_recipe_slug(name),
            **fields,
        }
    )
