from typing import Optional

from fastapi_camelcase import CamelModel

# from pydantic import EmailStr


class ChangePassword(CamelModel):
    current_password: str
    new_password: str


class UserBase(CamelModel):
    full_name: Optional[str] = None
    email: str
    family: str
    admin: bool

    class Config:
        schema_extra = {
            "fullName": "Change Me",
            "email": "changeme@email.com",
            "family": "public",
            "admin": "false",
        }


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    id: int


class UserInDB(UserIn, UserOut):
    pass
