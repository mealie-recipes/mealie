from uuid import uuid4

from sqlalchemy import Column, ForeignKey, String, orm

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import GUID, auto_init


class GroupDataExportsModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "group_data_exports"
    id = Column(GUID, primary_key=True, default=uuid4)

    group = orm.relationship("Group", back_populates="data_exports", single_parent=True)
    group_id = Column(GUID, ForeignKey("groups.id"), index=True)

    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)
    size = Column(String, nullable=False)
    expires = Column(String, nullable=False)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
