import sqlalchemy as sa
import sqlalchemy.orm as orm
from db.models.model_base import BaseMixins, SqlAlchemyBase
from db.models.recipe.category import Category, site_settings2categories
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

    def __init__(
        self, session: Session = None, language="en", categories: list = [], show_recent=True
    ) -> None:
        session.commit()
        self.language = language

        self.show_recent = show_recent
        self.categories = [
            Category.create_if_not_exist(session=session, name=cat.get("name"))
            for cat in categories
        ]

    def update(self, *args, **kwarg):
        self.__init__(*args, **kwarg)
