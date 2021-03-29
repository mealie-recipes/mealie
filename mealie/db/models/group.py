import sqlalchemy as sa
import sqlalchemy.orm as orm
from fastapi.logger import logger
from mealie.core.config import DEFAULT_GROUP
from mealie.db.models.model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models.recipe.category import Category, group2categories
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
        "MealPlanModel",
        back_populates="group",
        single_parent=True,
        order_by="MealPlanModel.startDate",
    )
    categories = orm.relationship("Category", secondary=group2categories, single_parent=True)

    # Webhook Settings
    webhook_enable = sa.Column(sa.Boolean, default=False)
    webhook_time = sa.Column(sa.String, default="00:00")
    webhook_urls = orm.relationship("WebhookURLModel", uselist=True, cascade="all, delete-orphan")

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
        self.categories = [Category.get_ref(session=session, slug=cat.get("slug")) for cat in categories]

        self.webhook_enable = webhook_enable
        self.webhook_time = webhook_time
        self.webhook_urls = [WebhookURLModel(url=x) for x in webhook_urls]

    def update(self, session: Session, *args, **kwargs):

        self.__init__(session=session, *args, **kwargs)

    @staticmethod
    def get_ref(session: Session, name: str):
        item = session.query(Group).filter(Group.name == name).one_or_none()
        if item is None:
            item = session.query(Group).filter(Group.id == 1).one()
        return item

    @staticmethod
    def create_if_not_exist(session, name: str = DEFAULT_GROUP):
        result = session.query(Group).filter(Group.name == name).one_or_none()
        if result:
            logger.info("Group exists, associating recipe")
            return result
        else:
            logger.info("Group doesn't exists, creating tag")
            return Group(name=name)
