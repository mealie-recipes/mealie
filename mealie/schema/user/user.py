from pathlib import Path
from typing import Any, Optional
from uuid import UUID

from pydantic import UUID4
from pydantic.types import constr
from pydantic.utils import GetterDict

from mealie.core.config import get_app_dirs, get_app_settings
from mealie.db.models.users import User
from mealie.schema._mealie import MealieModel
from mealie.schema.group.group_preferences import ReadGroupPreferences
from mealie.schema.recipe import RecipeSummary

from ..recipe import CategoryBase

settings = get_app_settings()


class LongLiveTokenIn(MealieModel):
    name: str


class LongLiveTokenOut(MealieModel):
    token: str
    name: str
    id: int

    class Config:
        orm_mode = True


class CreateToken(LongLiveTokenIn):
    user_id: UUID4
    token: str

    class Config:
        orm_mode = True


class DeleteTokenResponse(MealieModel):
    token_delete: str

    class Config:
        orm_mode = True


class ChangePassword(MealieModel):
    current_password: str
    new_password: str


class GroupBase(MealieModel):
    name: str

    class Config:
        orm_mode = True


class UserBase(MealieModel):
    username: Optional[str]
    full_name: Optional[str] = None
    email: constr(to_lower=True, strip_whitespace=True)  # type: ignore
    admin: bool = False
    group: Optional[str]
    advanced: bool = False
    favorite_recipes: Optional[list[str]] = []

    can_invite: bool = False
    can_manage: bool = False
    can_organize: bool = False

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
    id: UUID4
    group: str
    group_id: UUID4
    tokens: Optional[list[LongLiveTokenOut]]
    cache_key: str
    favorite_recipes: Optional[list[str]] = []

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(cls, ormModel: User):
            return {
                **GetterDict(ormModel),
                "group": ormModel.group.name,
                "favorite_recipes": [x.slug for x in ormModel.favorite_recipes],
            }


class UserFavorites(UserBase):
    favorite_recipes: list[RecipeSummary] = []  # type: ignore

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(cls, ormModel: User):
            return {
                **GetterDict(ormModel),
                "group": ormModel.group.name,
            }


class PrivateUser(UserOut):
    password: str
    group_id: UUID4

    class Config:
        orm_mode = True

    @staticmethod
    def get_directory(user_id: UUID4 | str) -> Path:
        user_dir = get_app_dirs().USER_DIR / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def directory(self) -> Path:
        return PrivateUser.get_directory(self.id)


class UpdateGroup(GroupBase):
    id: UUID4
    name: str
    categories: Optional[list[CategoryBase]] = []

    webhooks: list[Any] = []


class GroupInDB(UpdateGroup):
    users: Optional[list[UserOut]]
    preferences: Optional[ReadGroupPreferences] = None

    class Config:
        orm_mode = True

    @staticmethod
    def get_directory(id: UUID4) -> Path:
        dir = get_app_dirs().GROUPS_DIR / str(id)
        dir.mkdir(parents=True, exist_ok=True)
        return dir

    @staticmethod
    def get_export_directory(id: UUID) -> Path:
        dir = GroupInDB.get_directory(id) / "export"
        dir.mkdir(parents=True, exist_ok=True)
        return dir

    @property
    def directory(self) -> Path:
        return GroupInDB.get_directory(self.id)

    @property
    def exports(self) -> Path:
        return GroupInDB.get_export_directory(self.id)


class LongLiveTokenInDB(CreateToken):
    id: int
    user: PrivateUser

    class Config:
        orm_mode = True
