from typing import Optional

from pydantic import UUID4, BaseModel
from pydantic.types import constr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[UUID4]
    username: Optional[constr(to_lower=True, strip_whitespace=True)] = None
