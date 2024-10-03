from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, orm
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.datetime import NaiveDateTime
from mealie.db.models._model_utils.guid import GUID

from .._model_utils.auto_init import auto_init

if TYPE_CHECKING:
    from ..group import Group


class ServerTaskModel(SqlAlchemyBase, BaseMixins):
    # Server Tasks are deprecated, but the table still exists in the database

    __tablename__ = "server_tasks"
    name: Mapped[str] = mapped_column(String, nullable=False)
    completed_date: Mapped[datetime] = mapped_column(NaiveDateTime, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    log: Mapped[str] = mapped_column(String, nullable=True)

    group_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="server_tasks")

    @auto_init()
    def __init__(self, **_) -> None:
        pass
