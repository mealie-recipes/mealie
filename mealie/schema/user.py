from typing import Optional

from core.config import DEFAULT_GROUP
from db.models.users import User
from fastapi_camelcase import CamelModel
from pydantic.utils import GetterDict


class ChangePassword(CamelModel):
    current_password: str
    new_password: str


class GroupBase(CamelModel):
    name: str

    class Config:
        orm_mode = True


class UserBase(CamelModel):
    full_name: Optional[str] = None
    email: str
    admin: bool
    group: Optional[str]

    class Config:
        orm_mode = True

    class Config:
        schema_extra = {
            "fullName": "Change Me",
            "email": "changeme@email.com",
            "group": DEFAULT_GROUP,
            "admin": "false",
        }


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    group: str

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(cls, ormModel: User):
            return {
                **GetterDict(ormModel),
                "group": ormModel.group.name,
            }


class UserInDB(UserOut):
    password: str
    pass

    class Config:
        orm_mode = True


class GroupInDB(GroupBase):
    id: int
    name: str
    users: Optional[list[UserOut]]

    class Config:
        orm_mode = True
