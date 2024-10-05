from typing import Annotated

from fastapi import Form
from pydantic import UUID4, BaseModel, StringConstraints

from mealie.schema._mealie.mealie_model import MealieModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: UUID4 | None = None
    username: Annotated[str, StringConstraints(to_lower=True, strip_whitespace=True)] | None = None  # type: ignore


class UnlockResults(MealieModel):
    unlocked: int = 0


class CredentialsRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False


class CredentialsRequestForm:
    """Class that represents a user's credentials from the login form"""

    def __init__(
        self,
        username: str = Form(""),
        password: str = Form(""),
        remember_me: bool = Form(False),
    ):
        self.username = username
        self.password = password
        self.remember_me = remember_me
