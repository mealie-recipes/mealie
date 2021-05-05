from enum import unique

import sqlalchemy as sa
import sqlalchemy.orm as orm
from mealie.db.models.model_base import BaseMixins, SqlAlchemyBase
from sqlalchemy.sql.sqltypes import Integer


class SiteThemeModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "site_theme"
    id = sa.Column(Integer, primary_key=True, unique=True)
    name = sa.Column(sa.String, nullable=False, unique=True)
    colors = orm.relationship("ThemeColorsModel", uselist=False, cascade="all, delete")

    def __init__(self, name: str, colors: dict, *arg, **kwargs) -> None:
        self.name = name
        self.colors = ThemeColorsModel(**colors)


class ThemeColorsModel(SqlAlchemyBase, BaseMixins):
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
