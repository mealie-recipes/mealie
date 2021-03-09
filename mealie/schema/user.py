from typing import Any, Optional

from core.config import DEFAULT_GROUP
from db.models.group import WebHookModel
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


class Webhooks(CamelModel):
    webhookURLs: list[str] = []
    webhookTime: str = "00:00"
    enabled: bool = False

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(_cls, orm_model: WebHookModel):
            return {
                **GetterDict(orm_model),
                "webookURLs": [x.url for x in orm_model.webhookURLs],
            }


class GroupInDB(GroupBase):
    id: int
    name: str
    users: Optional[list[UserOut]]
    mealplans: Optional[list[MealPlanInDB]]
    categories: Optional[list[CategoryBase]]
    webhooks: Optional[Webhooks]

    class Config:
        orm_mode = True
