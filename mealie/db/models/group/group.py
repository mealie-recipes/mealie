import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_settings
from mealie.db.models.labels import MultiPurposeLabel

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import GUID, auto_init
from ..group.invite_tokens import GroupInviteToken
from ..group.webhooks import GroupWebhooksModel
from ..recipe.category import Category, group_to_categories
from ..server.task import ServerTaskModel
from .cookbook import CookBook
from .mealplan import GroupMealPlan
from .preferences import GroupPreferencesModel


class Group(SqlAlchemyBase, BaseMixins):
    __tablename__ = "groups"
    id = sa.Column(GUID, primary_key=True, default=GUID.generate)
    name = sa.Column(sa.String, index=True, nullable=False, unique=True)
    users = orm.relationship("User", back_populates="group")
    categories = orm.relationship(Category, secondary=group_to_categories, single_parent=True, uselist=True)

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

    labels = orm.relationship(MultiPurposeLabel, **common_args)

    mealplans = orm.relationship(GroupMealPlan, order_by="GroupMealPlan.date", **common_args)
    webhooks = orm.relationship(GroupWebhooksModel, **common_args)
    cookbooks = orm.relationship(CookBook, **common_args)
    server_tasks = orm.relationship(ServerTaskModel, **common_args)
    data_exports = orm.relationship("GroupDataExportsModel", **common_args)
    shopping_lists = orm.relationship("ShoppingList", **common_args)
    group_reports = orm.relationship("ReportModel", **common_args)
    group_event_notifiers = orm.relationship("GroupEventNotifierModel", **common_args)

    # Owned Models
    ingredient_units = orm.relationship("IngredientUnitModel", **common_args)
    ingredient_foods = orm.relationship("IngredientFoodModel", **common_args)
    tools = orm.relationship("Tool", **common_args)
    tags = orm.relationship("Tag", **common_args)
    categories = orm.relationship("Category", **common_args)

    class Config:
        exclude = {
            "users",
            "webhooks",
            "shopping_lists",
            "cookbooks",
            "preferences",
            "invite_tokens",
            "mealplans",
            "data_exports",
        }

    @auto_init()
    def __init__(self, **_) -> None:
        pass

    @staticmethod  # TODO: Remove this
    def get_ref(session: Session, name: str):  # type: ignore
        settings = get_app_settings()

        item = session.query(Group).filter(Group.name == name).one_or_none()
        if item is None:
            item = session.query(Group).filter(Group.name == settings.DEFAULT_GROUP).one()
        return item
