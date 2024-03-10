from datetime import datetime, timedelta
from pathlib import Path
from typing import Annotated
from uuid import UUID

from pydantic import UUID4, ConfigDict, Field, StringConstraints, field_validator
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.core.config import get_app_dirs, get_app_settings
from mealie.db.models.users import User
from mealie.db.models.users.users import AuthMethod
from mealie.schema._mealie import MealieModel
from mealie.schema.group.group_preferences import ReadGroupPreferences
from mealie.schema.group.webhook import CreateWebhook, ReadWebhook
from mealie.schema.recipe import RecipeSummary
from mealie.schema.response.pagination import PaginationBase

from ...db.models.group import Group
from ...db.models.recipe import RecipeModel
from ..recipe import CategoryBase

DEFAULT_INTEGRATION_ID = "generic"
settings = get_app_settings()


class LongLiveTokenIn(MealieModel):
    name: str
    integration_id: str = DEFAULT_INTEGRATION_ID


class LongLiveTokenOut(MealieModel):
    token: str
    name: str
    id: int
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class CreateToken(LongLiveTokenIn):
    user_id: UUID4
    token: str
    model_config = ConfigDict(from_attributes=True)


class DeleteTokenResponse(MealieModel):
    token_delete: str
    model_config = ConfigDict(from_attributes=True)


class ChangePassword(MealieModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class GroupBase(MealieModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]  # type: ignore
    model_config = ConfigDict(from_attributes=True)


class UserBase(MealieModel):
    id: UUID4 | None = None
    username: str | None = None
    full_name: str | None = None
    email: Annotated[str, StringConstraints(to_lower=True, strip_whitespace=True)]  # type: ignore
    auth_method: AuthMethod = AuthMethod.MEALIE
    admin: bool = False
    group: str | None = None
    advanced: bool = False
    favorite_recipes: list[str] | None = []

    can_invite: bool = False
    can_manage: bool = False
    can_organize: bool = False
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "ChangeMe",
                "fullName": "Change Me",
                "email": "changeme@example.com",
                "group": settings.DEFAULT_GROUP,
                "admin": "false",
            }
        },
    )

    @field_validator("group", mode="before")
    def convert_group_to_name(cls, v):
        if not v or isinstance(v, str):
            return v

        try:
            return v.name
        except AttributeError:
            return v


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    id: UUID4
    group: str
    group_id: UUID4
    group_slug: str
    tokens: list[LongLiveTokenOut] | None = None
    cache_key: str
    favorite_recipes: Annotated[list[str] | None, Field(validate_default=True)] = []
    model_config = ConfigDict(from_attributes=True)

    @property
    def is_default_user(self) -> bool:
        return self.email == settings._DEFAULT_EMAIL.strip().lower()

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [joinedload(User.group), joinedload(User.favorite_recipes), joinedload(User.tokens)]

    @field_validator("favorite_recipes", mode="before")
    def convert_favorite_recipes_to_slugs(cls, v):
        return [recipe.slug for recipe in v] if v else v


class UserPagination(PaginationBase):
    items: list[UserOut]


class UserFavorites(UserBase):
    favorite_recipes: list[RecipeSummary] = []  # type: ignore
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            joinedload(User.group),
            selectinload(User.favorite_recipes).joinedload(RecipeModel.recipe_category),
            selectinload(User.favorite_recipes).joinedload(RecipeModel.tags),
            selectinload(User.favorite_recipes).joinedload(RecipeModel.tools),
        ]


class PrivateUser(UserOut):
    password: str
    group_id: UUID4
    login_attemps: int = 0
    locked_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)

    @field_validator("login_attemps", mode="before")
    @classmethod
    def none_to_zero(cls, v):
        return 0 if v is None else v

    @staticmethod
    def get_directory(user_id: UUID4 | str) -> Path:
        user_dir = get_app_dirs().USER_DIR / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    @property
    def is_locked(self) -> bool:
        if self.locked_at is None:
            return False

        lockout_expires_at = self.locked_at + timedelta(hours=get_app_settings().SECURITY_USER_LOCKOUT_TIME)
        return lockout_expires_at > datetime.now()

    def directory(self) -> Path:
        return PrivateUser.get_directory(self.id)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [joinedload(User.group), selectinload(User.favorite_recipes), joinedload(User.tokens)]


class UpdateGroup(GroupBase):
    id: UUID4
    name: str
    slug: str
    categories: list[CategoryBase] | None = []

    webhooks: list[CreateWebhook] = []


class GroupInDB(UpdateGroup):
    users: list[UserOut] | None = None
    preferences: ReadGroupPreferences | None = None
    webhooks: list[ReadWebhook] = []

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def get_directory(id: UUID4) -> Path:
        group_dir = get_app_dirs().GROUPS_DIR / str(id)
        group_dir.mkdir(parents=True, exist_ok=True)
        return group_dir

    @staticmethod
    def get_export_directory(id: UUID) -> Path:
        export_dir = GroupInDB.get_directory(id) / "export"
        export_dir.mkdir(parents=True, exist_ok=True)
        return export_dir

    @property
    def directory(self) -> Path:
        return GroupInDB.get_directory(self.id)

    @property
    def exports(self) -> Path:
        return GroupInDB.get_export_directory(self.id)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            joinedload(Group.categories),
            joinedload(Group.webhooks),
            joinedload(Group.preferences),
            selectinload(Group.users).joinedload(User.group),
            selectinload(Group.users).joinedload(User.favorite_recipes),
            selectinload(Group.users).joinedload(User.tokens),
        ]


class GroupPagination(PaginationBase):
    items: list[GroupInDB]


class LongLiveTokenInDB(CreateToken):
    id: int
    user: PrivateUser
    model_config = ConfigDict(from_attributes=True)
