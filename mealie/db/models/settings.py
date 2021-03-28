import sqlalchemy as sa
import sqlalchemy.orm as orm
from mealie.db.models.model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models.recipe.category import Category, custom_pages2categories, site_settings2categories
from sqlalchemy.orm import Session


class SiteSettings(SqlAlchemyBase, BaseMixins):
    __tablename__ = "site_settings"
    id = sa.Column(sa.Integer, primary_key=True)
    language = sa.Column(sa.String)
    categories = orm.relationship(
        "Category",
        secondary=site_settings2categories,
        single_parent=True,
    )
    show_recent = sa.Column(sa.Boolean, default=True)
    cards_per_section = sa.Column(sa.Integer)

    def __init__(
        self,
        session: Session = None,
        language="en",
        categories: list = [],
        show_recent=True,
        cards_per_section: int = 9,
    ) -> None:
        session.commit()
        self.language = language
        self.cards_per_section = cards_per_section
        self.show_recent = show_recent
        self.categories = [Category.get_ref(session=session, slug=cat.get("slug")) for cat in categories]

    def update(self, *args, **kwarg):
        self.__init__(*args, **kwarg)


class CustomPage(SqlAlchemyBase, BaseMixins):
    __tablename__ = "custom_pages"
    id = sa.Column(sa.Integer, primary_key=True)
    position = sa.Column(sa.Integer, nullable=False)
    name = sa.Column(sa.String, nullable=False)
    slug = sa.Column(sa.String, nullable=False)
    categories = orm.relationship(
        "Category",
        secondary=custom_pages2categories,
        single_parent=True,
    )

    def __init__(self, session=None, name=None, slug=None, position=0, categories=[], *args, **kwargs) -> None:
        self.name = name
        self.slug = slug
        self.position = position
        self.categories = [Category.get_ref(session=session, slug=cat.get("slug")) for cat in categories]

    def update(self, *args, **kwarg):
        self.__init__(*args, **kwarg)
