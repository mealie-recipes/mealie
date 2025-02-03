from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated, Any, Generic, TypeVar
from uuid import UUID

from pydantic import UUID4, BaseModel, ConfigDict, Field, StringConstraints, field_validator
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.core.config import get_app_dirs, get_app_settings
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.users import User
from mealie.db.models.users.user_to_recipe import UserToRecipe
from mealie.db.models.users.users import AuthMethod, LongLiveToken
from mealie.schema._mealie import MealieModel
from mealie.schema.group.group_preferences import ReadGroupPreferences
from mealie.schema.household.webhook import CreateWebhook, ReadWebhook
from mealie.schema.response.pagination import PaginationBase

from ...db.models.group import Group
from ..recipe import CategoryBase

DataT = TypeVar("DataT", bound=BaseModel)
DEFAULT_INTEGRATION_ID = "generic"
settings = get_app_settings()


class LongLiveTokenIn(MealieModel):
    name: str
    integration_id: str = DEFAULT_INTEGRATION_ID


class LongLiveTokenOut(MealieModel):
    name: str
    id: int
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [joinedload(LongLiveToken.user)]


class LongLiveTokenCreateResponse(LongLiveTokenOut):
    """Should ONLY be used when creating a new token, as the token field is sensitive"""

    token: str


class CreateToken(LongLiveTokenIn):
    user_id: UUID4
    token: str
    model_config = ConfigDict(from_attributes=True)


class DeleteTokenResponse(MealieModel):
    token_delete: str
    model_config = ConfigDict(from_attributes=True)


class ChangePassword(MealieModel):
    current_password: str = ""
    new_password: str = Field(..., min_length=8)


class GroupBase(MealieModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    model_config = ConfigDict(from_attributes=True)


class UserRatingSummary(MealieModel):
    recipe_id: UUID4
    rating: float | None = None
    is_favorite: Annotated[bool, Field(validate_default=True)] = False

    model_config = ConfigDict(from_attributes=True)

    @field_validator("is_favorite", mode="before")
    def convert_is_favorite(cls, v: Any) -> bool:
        if v is None:
            return False
        else:
            return v


class UserRatingCreate(UserRatingSummary):
    user_id: UUID4


class UserRatingUpdate(MealieModel):
    rating: float | None = None
    is_favorite: bool | None = None


class UserRatingOut(UserRatingCreate):
    id: UUID4

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            joinedload(UserToRecipe.recipe).joinedload(RecipeModel.user).load_only(User.household_id, User.group_id)
        ]


class UserRatings(BaseModel, Generic[DataT]):
    ratings: list[DataT]


class UserBase(MealieModel):
    id: UUID4 | None = None
    username: str | None = None
    full_name: str | None = None
    email: Annotated[str, StringConstraints(to_lower=True, strip_whitespace=True)]
    auth_method: AuthMethod = AuthMethod.MEALIE
    admin: bool = False
    group: str | None = None
    household: str | None = None
    advanced: bool = False

    can_invite: bool = False
    can_manage: bool = False
    can_manage_household: bool = False
    can_organize: bool = False
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "ChangeMe",
                "fullName": "Change Me",
                "email": "changeme@example.com",
                "group": settings.DEFAULT_GROUP,
                "household": settings.DEFAULT_HOUSEHOLD,
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

    @field_validator("household", mode="before")
    def convert_household_to_name(cls, v):
        if not v or isinstance(v, str):
            return v

        try:
            return v.name
        except AttributeError:
            return v


class UserIn(UserBase):
    username: str
    full_name: str
    password: str


class UserOut(UserBase):
    id: UUID4
    group: str
    group_id: UUID4
    group_slug: str
    household: str
    household_id: UUID4
    household_slug: str
    tokens: list[LongLiveTokenOut] | None = None
    cache_key: str
    model_config = ConfigDict(from_attributes=True)

    @property
    def is_default_user(self) -> bool:
        return self.email == settings._DEFAULT_EMAIL.strip().lower()

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [joinedload(User.group), joinedload(User.household), joinedload(User.tokens)]


class UserSummary(MealieModel):
    id: UUID4
    group_id: UUID4
    household_id: UUID4
    username: str
    full_name: str
    model_config = ConfigDict(from_attributes=True)


class UserPagination(PaginationBase):
    items: list[UserOut]


class UserSummaryPagination(PaginationBase):
    items: list[UserSummary]


class PrivateUser(UserOut):
    password: str
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
        return lockout_expires_at > datetime.now(UTC)

    def directory(self) -> Path:
        return PrivateUser.get_directory(self.id)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [joinedload(User.group), joinedload(User.household), joinedload(User.tokens)]


class UpdateGroup(GroupBase):
    id: UUID4
    name: str
    slug: str
    categories: list[CategoryBase] | None = []

    webhooks: list[CreateWebhook] = []


class GroupHouseholdSummary(MealieModel):
    id: UUID4
    name: str
    model_config = ConfigDict(from_attributes=True)


class GroupInDB(UpdateGroup):
    households: list[GroupHouseholdSummary] | None = None
    users: list[UserSummary] | None = None
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
            joinedload(Group.households),
            selectinload(Group.users).joinedload(User.group),
            selectinload(Group.users).joinedload(User.tokens),
        ]


class GroupSummary(GroupBase):
    id: UUID4
    name: str
    slug: str
    preferences: ReadGroupPreferences | None = None

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            joinedload(Group.preferences),
        ]


class GroupPagination(PaginationBase):
    items: list[GroupInDB]


class LongLiveTokenInDB(CreateToken):
    id: int
    user: PrivateUser
    model_config = ConfigDict(from_attributes=True)
