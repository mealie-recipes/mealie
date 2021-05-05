import sqlalchemy.orm as orm
from mealie.db.models.model_base import BaseMixins, SqlAlchemyBase
from sqlalchemy import Column, ForeignKey, Integer, String


class SiteThemeModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "site_theme"
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, nullable=False, unique=True)
    colors = orm.relationship("ThemeColorsModel", uselist=False, single_parent=True, cascade="all, delete-orphan")

    def __init__(self, name: str, colors: dict, *arg, **kwargs) -> None:
        self.name = name
        self.colors = ThemeColorsModel(**colors)


class ThemeColorsModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "theme_colors"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("site_theme.id"))
    primary = Column(String)
    accent = Column(String)
    secondary = Column(String)
    success = Column(String)
    info = Column(String)
    warning = Column(String)
    error = Column(String)
