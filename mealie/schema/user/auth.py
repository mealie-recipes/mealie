from typing import Optional

from pydantic import BaseModel
from pydantic.types import constr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[constr(to_lower=True, strip_whitespace=True)] = None
