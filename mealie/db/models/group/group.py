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
    mealplans = orm.relationship(
        GroupMealPlan, back_populates="group", single_parent=True, order_by="GroupMealPlan.date"
    )
    webhooks = orm.relationship(GroupWebhooksModel, uselist=True, cascade="all, delete-orphan")
    cookbooks = orm.relationship(CookBook, back_populates="group", single_parent=True)
    server_tasks = orm.relationship(ServerTaskModel, back_populates="group", single_parent=True)
    shopping_lists = orm.relationship("ShoppingList", back_populates="group", single_parent=True)

    @auto_init({"users", "webhooks", "shopping_lists", "cookbooks", "preferences", "invite_tokens", "mealplans"})
    def __init__(self, **_) -> None:
        pass

    @staticmethod
    def get_ref(session: Session, name: str):
        item = session.query(Group).filter(Group.name == name).one_or_none()
        if item is None:
            item = session.query(Group).filter(Group.name == settings.DEFAULT_GROUP).one()
        return item
