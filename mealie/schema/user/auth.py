from typing import Annotated

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
