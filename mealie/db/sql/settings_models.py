import sqlalchemy as sa
import sqlalchemy.orm as orm
from db.sql.model_base import SqlAlchemyBase


class WebhookURLModel(SqlAlchemyBase):
    __tablename__ = "webhook_urls"
    id = sa.Column(sa.Integer, primary_key=True)
    url = sa.Column(sa.String)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("webhook_settings.id"))

    def update(self, url) -> str:
        self.url = url

    def to_str(self):
        return self.url


class WebHookModel(SqlAlchemyBase):
    __tablename__ = "webhook_settings"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("site_settings.name"))
    webhookURLs = orm.relationship(
        "WebhookURLModel", uselist=True, cascade="all, delete"
    )
    webhookTime = sa.Column(sa.String, default="00:00")
    enabled = sa.Column(sa.Boolean, default=False)

    def __init__(
        self, webhookURLs: list, webhookTime: str, enabled: bool = False
    ) -> None:
        self.webhookURLs = [WebhookURLModel(x) for x in webhookURLs]
        self.webhookTime = webhookTime
        self.enabled = enabled

    def update(self, webhookURLs: list, webhookTime: str, enabled: bool) -> None:
        current_webhooks = 0

        for webhook_url in self.webhookURLs:
            try:
                webhook_url.update(webhookURLs[current_webhooks])
                current_webhooks += 1
            except:
                self.webhookURLs.remove(webhook_url)

        for webhook_url in webhookURLs[current_webhooks:]:
            self.webhookURLs.append(WebhookURLModel(webhook_url))

        self.webhookTime = webhookTime
        self.enabled = enabled

    def dict(self):
        data = {
            "webhookURLs": [url.to_str() for url in self.webhookURLs],
            "webhookTime": self.webhookTime,
            "enabled": self.enabled,
        }
        return data


class SiteSettingsModel(SqlAlchemyBase):
    __tablename__ = "site_settings"
    name = sa.Column(sa.String, primary_key=True)
    webhooks = orm.relationship("WebHookModel", uselist=False, cascade="all, delete")

    def __init__(self, name: str = None, webhooks: dict = None) -> None:
        self.name = name
        self.webhooks = WebHookModel(**webhooks)

    def update(self, name, webhooks: dict) -> dict:
        self.name = name
        self.webhooks.update(**webhooks)
        return

    def dict(self):
        data = {"name": self.name, "webhooks": self.webhooks.dict()}
        return data


class ThemeColorsModel(SqlAlchemyBase):
    __tablename__ = "theme_colors"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("site_theme.name"))
    primary = sa.Column(sa.String)
    accent = sa.Column(sa.String)
    secondary = sa.Column(sa.String)
    success = sa.Column(sa.String)
    info = sa.Column(sa.String)
    warning = sa.Column(sa.String)
    error = sa.Column(sa.String)

    def update(
        self,
        primary: str = None,
        accent: str = None,
        secondary: str = None,
        success: str = None,
        info: str = None,
        warning: str = None,
        error: str = None,
    ) -> None:
        self.primary = primary
        self.accent = accent
        self.secondary = secondary
        self.success = success
        self.info = info
        self.warning = warning
        self.error = error

    def dict(self):
        data = {
            "primary": self.primary,
            "accent": self.accent,
            "secondary": self.secondary,
            "success": self.success,
            "info": self.info,
            "warning": self.warning,
            "error": self.error,
        }
        return data


class SiteThemeModel(SqlAlchemyBase):
    __tablename__ = "site_theme"
    name = sa.Column(sa.String, primary_key=True)
    colors = orm.relationship("ThemeColorsModel", uselist=False, cascade="all, delete")

    def __init__(self, name: str, colors: dict) -> None:
        self.name = name
        self.colors = ThemeColorsModel(**colors)

    def update(self, name, colors: dict) -> dict:
        self.colors.update(**colors)
        return self.dict()

    def dict(self):
        data = {"name": self.name, "colors": self.colors.dict()}
        return data
