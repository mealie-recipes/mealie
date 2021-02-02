import sqlalchemy as sa
import sqlalchemy.orm as orm
from db.sql.model_base import BaseMixins, SqlAlchemyBase


class SiteThemeModel(SqlAlchemyBase):
    __tablename__ = "site_theme"
    name = sa.Column(sa.String, primary_key=True)
    colors = orm.relationship("ThemeColorsModel", uselist=False, cascade="all, delete")

    def __init__(self, name: str, colors: dict) -> None:
        self.name = name
        self.colors = ThemeColorsModel(**colors)

    def update(self, session=None, name: str = None, colors: dict = None) -> dict:
        self.colors.update(**colors)
        return self.dict()

    def dict(self):
        data = {"name": self.name, "colors": self.colors.dict()}
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
