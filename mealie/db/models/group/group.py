import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_settings
from mealie.db.models.group.invite_tokens import GroupInviteToken
from mealie.db.models.server.task import ServerTaskModel

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import auto_init
from ..group.webhooks import GroupWebhooksModel
from ..recipe.category import Category, group2categories
from .cookbook import CookBook
from .mealplan import GroupMealPlan
from .preferences import GroupPreferencesModel

settings = get_app_settings()


class Group(SqlAlchemyBase, BaseMixins):
    __tablename__ = "groups"
    name = sa.Column(sa.String, index=True, nullable=False, unique=True)
    users = orm.relationship("User", back_populates="group")
    categories = orm.relationship(Category, secondary=group2categories, single_parent=True, uselist=True)

    invite_tokens = orm.relationship(
        GroupInviteToken, back_populates="group", cascade="all, delete-orphan", uselist=True
    )
    preferences = orm.relationship(
        GroupPreferencesModel,
        back_populates="group",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
    )

    # Recipes
    recipes = orm.relationship("RecipeModel", back_populates="group", uselist=True)

    # CRUD From Others
    common_args = {
        "back_populates": "group",
        "cascade": "all, delete-orphan",
        "single_parent": True,
    }

    mealplans = orm.relationship(GroupMealPlan, order_by="GroupMealPlan.date", **common_args)
    webhooks = orm.relationship(GroupWebhooksModel, **common_args)
    cookbooks = orm.relationship(CookBook, **common_args)
    server_tasks = orm.relationship(ServerTaskModel, **common_args)
    shopping_lists = orm.relationship("ShoppingList", **common_args)
    group_reports = orm.relationship("ReportModel", **common_args)

    class Config:
        exclude = {"users", "webhooks", "shopping_lists", "cookbooks", "preferences", "invite_tokens", "mealplans"}

    @auto_init()
    def __init__(self, **_) -> None:
        pass

    @staticmethod
    def get_ref(session: Session, name: str):
        item = session.query(Group).filter(Group.name == name).one_or_none()
        if item is None:
            item = session.query(Group).filter(Group.name == settings.DEFAULT_GROUP).one()
        return item
