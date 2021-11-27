from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, orm

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase

from .._model_utils import auto_init


class GroupWebhooksModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "webhook_urls"
    id = Column(Integer, primary_key=True)

    group = orm.relationship("Group", back_populates="webhooks", single_parent=True)
    group_id = Column(Integer, ForeignKey("groups.id"), index=True)

    enabled = Column(Boolean, default=False)
    name = Column(String)
    url = Column(String)
    time = Column(String, default="00:00")

    @auto_init()
    def __init__(self, **_) -> None:
        pass
