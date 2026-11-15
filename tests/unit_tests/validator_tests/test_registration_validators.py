import pytest

from mealie.schema.user.registration import UserRegistrationCreate


def test_create_user_registration() -> None:
    UserRegistrationCreate(
        group="Home",
        household="Family",
        group_token=None,
        email="SomeValidEmail@example.com",
        username="SomeValidUsername",
        full_name="SomeValidFullName",
        password="SomeValidPassword",
        password_confirm="SomeValidPassword",
        advanced=False,
        private=True,
    )

    UserRegistrationCreate(
        group=None,
        household=None,
        group_token="asdfadsfasdfasdfasdf",
        email="SomeValidEmail@example.com",
        username="SomeValidUsername",
        full_name="SomeValidFullName",
        password="SomeValidPassword",
        password_confirm="SomeValidPassword",
        advanced=False,
        private=True,
    )


@pytest.mark.parametrize("group", [None, ""])
@pytest.mark.parametrize("household", [None, ""])
@pytest.mark.parametrize("group_token", [None, ""])
def test_group_or_token_validator(group, household, group_token) -> None:
    with pytest.raises(ValueError):
        UserRegistrationCreate(
            group=group,
            household=household,
            group_token=group_token,
            email="SomeValidEmail@example.com",
            username="SomeValidUsername",
            full_name="SomeValidFullName",
            password="SomeValidPassword",
            password_confirm="SomeValidPassword",
            advanced=False,
            private=True,
        )


def test_group_no_args_passed() -> None:
    with pytest.raises(ValueError):
        UserRegistrationCreate(
            email="SomeValidEmail@example.com",
            username="SomeValidUsername",
            full_name="SomeValidFullName",
            password="SomeValidPassword",
            password_confirm="SomeValidPassword",
            advanced=False,
            private=True,
        )


def test_password_validator() -> None:
    with pytest.raises(ValueError):
        UserRegistrationCreate(
            group=None,
            household=None,
            group_token="asdfadsfasdfasdfasdf",
            email="SomeValidEmail@example.com",
            username="SomeValidUsername",
            full_name="SomeValidFullName",
            password="SomeValidPassword",
            password_confirm="PasswordDefNotMatch",
            advanced=False,
            private=True,
        )
