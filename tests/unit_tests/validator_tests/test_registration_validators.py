import pytest

from mealie.schema.user.registration import CreateUserRegistration


def test_create_user_registration() -> None:
    CreateUserRegistration(
        group="Home",
        group_token=None,
        email="SomeValidEmail@email.com",
        username="SomeValidUsername",
        password="SomeValidPassword",
        password_confirm="SomeValidPassword",
        advanced=False,
        private=True,
    )

    CreateUserRegistration(
        group=None,
        group_token="asdfadsfasdfasdfasdf",
        email="SomeValidEmail@email.com",
        username="SomeValidUsername",
        password="SomeValidPassword",
        password_confirm="SomeValidPassword",
        advanced=False,
        private=True,
    )


@pytest.mark.parametrize("group, group_token", [(None, None), ("", None), (None, "")])
def test_group_or_token_validator(group, group_token) -> None:
    with pytest.raises(ValueError):
        CreateUserRegistration(
            group=group,
            group_token=group_token,
            email="SomeValidEmail@email.com",
            username="SomeValidUsername",
            password="SomeValidPassword",
            password_confirm="SomeValidPassword",
            advanced=False,
            private=True,
        )


def test_group_no_args_passed() -> None:
    with pytest.raises(ValueError):
        CreateUserRegistration(
            email="SomeValidEmail@email.com",
            username="SomeValidUsername",
            password="SomeValidPassword",
            password_confirm="SomeValidPassword",
            advanced=False,
            private=True,
        )


def test_password_validator() -> None:
    with pytest.raises(ValueError):
        CreateUserRegistration(
            group=None,
            group_token="asdfadsfasdfasdfasdf",
            email="SomeValidEmail@email.com",
            username="SomeValidUsername",
            password="SomeValidPassword",
            password_confirm="PasswordDefNotMatch",
            advanced=False,
            private=True,
        )


test_create_user_registration()
