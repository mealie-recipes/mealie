import random
import string

from mealie.schema.user.registration import CreateUserRegistration


def random_string(length=10) -> str:
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length)).strip()


def random_email(length=10) -> str:
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length)) + "@fake.com"


def random_bool() -> bool:
    return bool(random.getrandbits(1))


def user_registration_factory() -> CreateUserRegistration:
    return CreateUserRegistration(
        group=random_string(),
        email=random_email(),
        username=random_string(),
        password="fake-password",
        password_confirm="fake-password",
        advanced=False,
        private=False,
    )
