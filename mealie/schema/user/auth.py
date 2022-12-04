from pydantic import UUID4, BaseModel
from pydantic.types import constr

from mealie.schema._mealie.mealie_model import MealieModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: UUID4 | None
    username: constr(to_lower=True, strip_whitespace=True) | None = None  # type: ignore


class UnlockResults(MealieModel):
    unlocked: int = 0
