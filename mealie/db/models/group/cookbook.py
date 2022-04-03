from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, orm

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import auto_init, guid
from ..recipe.category import Category, cookbooks_to_categories
from ..recipe.tag import Tag, cookbooks_to_tags
from ..recipe.tool import Tool, cookbooks_to_tools


class CookBook(SqlAlchemyBase, BaseMixins):
    __tablename__ = "cookbooks"
    id = Column(guid.GUID, primary_key=True, default=guid.GUID.generate)
    position = Column(Integer, nullable=False, default=1)

    group_id = Column(guid.GUID, ForeignKey("groups.id"))
    group = orm.relationship("Group", back_populates="cookbooks")

    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    description = Column(String, default="")
    public = Column(Boolean, default=False)

    categories = orm.relationship(Category, secondary=cookbooks_to_categories, single_parent=True)
    require_all_categories = Column(Boolean, default=True)

    tags = orm.relationship(Tag, secondary=cookbooks_to_tags, single_parent=True)
    require_all_tags = Column(Boolean, default=True)

    tools = orm.relationship(Tool, secondary=cookbooks_to_tools, single_parent=True)
    require_all_tools = Column(Boolean, default=True)

    @auto_init()
    def __init__(self, **_) -> None:
        pass

    def update(self, *args, **kwarg):
        self.__init__(*args, **kwarg)
