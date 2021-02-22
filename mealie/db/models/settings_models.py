import sqlalchemy as sa
import sqlalchemy.orm as orm
from db.models.model_base import BaseMixins, SqlAlchemyBase
from db.models.recipe_models import Category


class SiteSettingsModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "site_settings"
    name = sa.Column(sa.String, primary_key=True)
    planCategories = orm.relationship(
        "MealCategory", uselist=True, cascade="all, delete"
    )
    webhooks = orm.relationship("WebHookModel", uselist=False, cascade="all, delete")

    def __init__(
        self, name: str = None, webhooks: dict = None, planCategories=[], session=None
    ) -> None:
        self.name = name
        self.planCategories = [MealCategory(cat) for cat in planCategories]
        self.webhooks = WebHookModel(**webhooks)

    def update(self, session, name, webhooks: dict, planCategories=[]) -> dict:

        self._sql_remove_list(session, [MealCategory], self.name)
        self.name = name
        self.planCategories = [MealCategory(x) for x in planCategories]
        self.webhooks.update(session=session, **webhooks)
        return

    def dict(self):
        data = {
            "name": self.name,
            "planCategories": [cat.to_str() for cat in self.planCategories],
            "webhooks": self.webhooks.dict(),
        }
        return data


class MealCategory(SqlAlchemyBase):
    __tablename__ = "meal_plan_categories"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("site_settings.name"))

    def __init__(self, name) -> None:
        self.name = name

    def to_str(self):
        return self.name


class WebHookModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "webhook_settings"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("site_settings.name"))
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

    def dict(self):
        data = {
            "webhookURLs": [url.to_str() for url in self.webhookURLs],
            "webhookTime": self.webhookTime,
            "enabled": self.enabled,
        }
        return data


class WebhookURLModel(SqlAlchemyBase):
    __tablename__ = "webhook_urls"
    id = sa.Column(sa.Integer, primary_key=True)
    url = sa.Column(sa.String)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("webhook_settings.id"))

    def to_str(self):
        return self.url
