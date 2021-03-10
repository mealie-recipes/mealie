import sqlalchemy as sa
import sqlalchemy.orm as orm
from core.config import DEFAULT_GROUP
from db.models.model_base import BaseMixins, SqlAlchemyBase
from db.models.recipe.category import Category, group2categories
from fastapi.logger import logger
from sqlalchemy.orm.session import Session


class WebhookURLModel(SqlAlchemyBase):
    __tablename__ = "webhook_urls"
    id = sa.Column(sa.Integer, primary_key=True)
    url = sa.Column(sa.String)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("groups.id"))


class Group(SqlAlchemyBase, BaseMixins):
    __tablename__ = "groups"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, index=True, nullable=False, unique=True)
    users = orm.relationship("User", back_populates="group")
    mealplans = orm.relationship(
        "MealPlanModel", back_populates="group", single_parent=True
    )
    mealplan_categories = orm.relationship(
        "Category", secondary=group2categories, single_parent=True
    )

    # Webhook Settings
    webhook_enable = sa.Column(sa.Boolean, default=False)
    webhook_time = sa.Column(sa.String, default="00:00")
    webhook_urls = orm.relationship(
        "WebhookURLModel", uselist=True, cascade="all, delete"
    )

    def __init__(
        self,
        name,
        id=None,
        users=None,
        mealplans=None,
        categories=[],
        session=None,
        webhook_enable=False,
        webhook_time="00:00",
        webhook_urls=[],
    ) -> None:
        self.name = name
        self.categories = [
            Category.create_if_not_exist(session=session, name=cat.get("name"))
            for cat in categories
        ]

        self.webhook_enable = webhook_enable
        self.webhook_time = webhook_time
        self.webhook_urls = [WebhookURLModel(url=x) for x in webhook_urls]

    def update(self, session: Session, *args, **kwargs):
        self._sql_remove_list(session, [WebhookURLModel], self.id)

        self.__init__(*args, **kwargs)

    @staticmethod
    def create_if_not_exist(session, name: str = DEFAULT_GROUP):
        try:
            result = session.query(Group).filter(Group.name == name).one()
            if result:
                logger.info("Category exists, associating recipe")
                return result
            else:
                logger.info("Category doesn't exists, creating tag")
                return Group(name=name)
        except:
            logger.info("Category doesn't exists, creating category")
            return Group(name=name)
