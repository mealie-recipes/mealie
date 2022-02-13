from sqlalchemy import Column, DateTime, ForeignKey, String, orm

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID

from .._model_utils import auto_init


class ServerTaskModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "server_tasks"
    name = Column(String, nullable=False)
    completed_date = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)
    log = Column(String, nullable=True)

    group_id = Column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group = orm.relationship("Group", back_populates="server_tasks")

    @auto_init()
    def __init__(self, **_) -> None:
        pass
