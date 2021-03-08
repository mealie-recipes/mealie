import sqlalchemy as sa
import sqlalchemy.orm as orm
from db.models.model_base import BaseMixins, SqlAlchemyBase
from db.models.recipe.category import Category, sidebar2categories
from sqlalchemy.orm import Session


class Sidebar(SqlAlchemyBase, BaseMixins):
    __tablename__ = "site_sidebar"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey("site_settings.id"))
    categories = orm.relationship("Category", secondary=sidebar2categories, cascade="delete")

    def __init__(self, session: Session, sidebar: dict) -> None:
        categories = sidebar.get("categories")
        new_categories = []
        if not categories:
            return None
        for cat in categories:
            slug = cat.get("slug")
            cat_in_db = session.query(Category).filter(Category.slug == slug).one()
            new_categories.append(cat_in_db)

        self.categories = new_categories


class SiteSettings(SqlAlchemyBase, BaseMixins):
    __tablename__ = "site_settings"
    id = sa.Column(sa.Integer, primary_key=True)
    language = sa.Column(sa.String)
    sidebar = orm.relationship("Sidebar", uselist=False, cascade="all")

    def __init__(
        self, session=None, language="en", sidebar: list = {"categories": []}
    ) -> None:
        self._sql_remove_list(session, [Sidebar], self.id)

        self.language = language
        self.sidebar = Sidebar(session, sidebar)

    def update(self, session, language, sidebar):
        self.__init__(session=session, language=language, sidebar=sidebar)
