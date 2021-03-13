from typing import Any, Optional

from core.config import DEFAULT_GROUP
from db.models.group import Group
from db.models.users import User
from fastapi_camelcase import CamelModel
from pydantic.utils import GetterDict

from schema.category import CategoryBase
from schema.meal import MealPlanInDB


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

        @classmethod
        def getter_dict(_cls, name_orm: User):
            return {
                **GetterDict(name_orm),
                "group": name_orm.group.name,
            }

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


class UpdateGroup(GroupBase):
    id: int
    name: str
    categories: Optional[list[CategoryBase]] = []

    webhook_urls: list[str] = []
    webhook_time: str = "00:00"
    webhook_enable: bool


class GroupInDB(UpdateGroup):
    users: Optional[list[UserOut]]
    mealplans: Optional[list[MealPlanInDB]]

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(_cls, orm_model: Group):
            return {
                **GetterDict(orm_model),
                "webhook_urls": [x.url for x in orm_model.webhook_urls if x],
            }
