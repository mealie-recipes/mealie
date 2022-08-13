from typing import Optional

from pydantic import UUID4, BaseModel
from pydantic.types import constr

from mealie.schema._mealie.mealie_model import MealieModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[UUID4]
    username: Optional[constr(to_lower=True, strip_whitespace=True)] = None  # type: ignore


class UnlockResults(MealieModel):
    unlocked: int = 0
