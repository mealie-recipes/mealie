import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm.session import Session

from mealie.core.config import settings
from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models.cookbook import CookBook
from mealie.db.models.group.webhooks import GroupWebhooksModel
from mealie.db.models.recipe.category import Category, group2categories

from .._model_utils import auto_init


class Group(SqlAlchemyBase, BaseMixins):
    __tablename__ = "groups"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, index=True, nullable=False, unique=True)
    users = orm.relationship("User", back_populates="group")
    categories = orm.relationship(Category, secondary=group2categories, single_parent=True)

    # CRUD From Others
    mealplans = orm.relationship("MealPlan", back_populates="group", single_parent=True, order_by="MealPlan.start_date")
    webhooks = orm.relationship(GroupWebhooksModel, uselist=True, cascade="all, delete-orphan")
    cookbooks = orm.relationship(CookBook, back_populates="group", single_parent=True)
    shopping_lists = orm.relationship("ShoppingList", back_populates="group", single_parent=True)

    @auto_init({"users", "webhooks", "shopping_lists", "cookbooks"})
    def __init__(self, **_) -> None:
        pass

    @staticmethod
    def get_ref(session: Session, name: str):
        item = session.query(Group).filter(Group.name == name).one_or_none()
        if item is None:
            item = session.query(Group).filter(Group.name == settings.DEFAULT_GROUP).one()
        return item
