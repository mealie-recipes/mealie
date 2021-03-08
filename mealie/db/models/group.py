import sqlalchemy as sa
import sqlalchemy.orm as orm
from core.config import DEFAULT_GROUP
from db.models.model_base import BaseMixins, SqlAlchemyBase
from db.models.recipe.category import group2categories
from fastapi.logger import logger


class Group(SqlAlchemyBase, BaseMixins):
    __tablename__ = "groups"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, index=True, nullable=False, unique=True)
    users = orm.relationship("User", back_populates="group")
    mealplans = orm.relationship("MealPlanModel", back_populates="group")
    categories = orm.relationship("Category", secondary=group2categories)
    webhooks = orm.relationship("WebHookModel", uselist=False, cascade="all, delete")

    def __init__(self, name, session=None) -> None:
        self.name = name

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


class WebHookModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "webhook_settings"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("groups.id"))
    webhookURLs = orm.relationship(
        "WebhookURLModel", uselist=True, cascade="all, delete"
    )
    webhookTime = sa.Column(sa.String, default="00:00")
    enabled = sa.Column(sa.Boolean, default=False)

    def __init__(
        self, webhookURLs: list, webhookTime: str, enabled: bool = False, session=None
    ) -> None:

        self.webhookURLs = [WebhookURLModel(url=x) for x in webhookURLs]
        self.webhookTime = webhookTime
        self.enabled = enabled

    def update(
        self, session, webhookURLs: list, webhookTime: str, enabled: bool
    ) -> None:

        self._sql_remove_list(session, [WebhookURLModel], self.id)

        self.__init__(webhookURLs, webhookTime, enabled)


class WebhookURLModel(SqlAlchemyBase):
    __tablename__ = "webhook_urls"
    id = sa.Column(sa.Integer, primary_key=True)
    url = sa.Column(sa.String)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("webhook_settings.id"))
