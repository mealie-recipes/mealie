from typing import Optional

from fastapi_camelcase import CamelModel
from mealie.core.config import settings
from mealie.db.models.group import Group
from mealie.db.models.users import User
from mealie.schema.category import CategoryBase
from mealie.schema.meal import MealPlanOut
from mealie.schema.shopping_list import ShoppingListOut
from pydantic.types import constr
from pydantic.utils import GetterDict


class LoingLiveTokenIn(CamelModel):
    name: str


class LongLiveTokenOut(LoingLiveTokenIn):
    id: int

    class Config:
        orm_mode = True


class CreateToken(LoingLiveTokenIn):
    parent_id: int
    token: str

    class Config:
        orm_mode = True


class ChangePassword(CamelModel):
    current_password: str
    new_password: str


class GroupBase(CamelModel):
    name: str

    class Config:
        orm_mode = True


class UserBase(CamelModel):
    username: Optional[str]
    full_name: Optional[str] = None
    email: constr(to_lower=True, strip_whitespace=True)
    admin: bool
    group: Optional[str]

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(cls, name_orm: User):
            return {
                **GetterDict(name_orm),
                "group": name_orm.group.name,
            }

        schema_extra = {
            "username": "ChangeMe",
            "fullName": "Change Me",
            "email": "changeme@email.com",
            "group": settings.DEFAULT_GROUP,
            "admin": "false",
        }


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    group: str
    tokens: Optional[list[LongLiveTokenOut]]

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
    mealplans: Optional[list[MealPlanOut]]
    shopping_lists: Optional[list[ShoppingListOut]]

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(_cls, orm_model: Group):
            return {
                **GetterDict(orm_model),
                "webhook_urls": [x.url for x in orm_model.webhook_urls if x],
            }


class LongLiveTokenInDB(CreateToken):
    id: int
    user: UserInDB

    class Config:
        orm_mode = True
