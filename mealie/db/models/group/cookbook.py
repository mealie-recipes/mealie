from sqlalchemy import Column, ForeignKey, Integer, String, orm

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import auto_init, guid
from ..recipe.category import Category, cookbooks_to_categories


class CookBook(SqlAlchemyBase, BaseMixins):
    __tablename__ = "cookbooks"
    id = Column(Integer, primary_key=True)
    position = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    slug = Column(String, nullable=False)
    categories = orm.relationship(Category, secondary=cookbooks_to_categories, single_parent=True)

    group_id = Column(guid.GUID, ForeignKey("groups.id"))
    group = orm.relationship("Group", back_populates="cookbooks")

    @auto_init()
    def __init__(self, **_) -> None:
        pass

    def update(self, *args, **kwarg):
        self.__init__(*args, **kwarg)
