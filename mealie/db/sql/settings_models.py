import sqlalchemy as sa
import sqlalchemy.orm as orm
from db.sql.model_base import SqlAlchemyBase
from sqlalchemy.sql.expression import true


class WebhookURLModel(SqlAlchemyBase):
    __tablename__ = "webhook_urls"
    url = sa.Column(sa.String, primary_key=True, unique=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("webhook_settings.id"))

    def dict(self):
        return self.url


class WebHookModel(SqlAlchemyBase):
    __tablename__ = "webhook_settings"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("site_settings.name"))
    webhookURLs = orm.relation("WebhookURLModel")
    webhookTime = sa.Column(sa.String, default="00:00")
    enabled = sa.Column(sa.Boolean, default=False)

    def dict(self):
        data = {
            "webhookURLs": [url.dict for url in self.webhookURLS],
            "webhookTime": self.webhookTime,
            "enabled": self.enabled,
        }
        return data


class SiteSettingsModel(SqlAlchemyBase):
    __tablename__ = "site_settings"
    name = sa.Column(sa.String, primary_key=True)
    webhooks = orm.relation("WebHookModel")

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

    def dict(self):
        data = {"name": self.name, "colors": self.colors.dict()}
        return data
