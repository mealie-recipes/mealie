from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, String, Time, orm

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import GUID, auto_init


class GroupWebhooksModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "webhook_urls"
    id = Column(GUID, primary_key=True, default=GUID.generate)

    group = orm.relationship("Group", back_populates="webhooks", single_parent=True)
    group_id = Column(GUID, ForeignKey("groups.id"), index=True)

    enabled = Column(Boolean, default=False)
    name = Column(String)
    url = Column(String)

    # New Fields
    webhook_type = Column(String, default="")  # Future use for different types of webhooks
    scheduled_time = Column(Time, default=lambda: datetime.now().time())

    # Columne is no longer used but is kept for since it's super annoying to
    # delete a column in SQLite and it's not a big deal to keep it around
    time = Column(String, default="00:00")

    @auto_init()
    def __init__(self, **_) -> None:
        ...
