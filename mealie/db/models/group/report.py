from datetime import datetime, timezone
from typing import TYPE_CHECKING

from pydantic import ConfigDict
from sqlalchemy import ForeignKey, orm
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Boolean, DateTime, String

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase

from .._model_utils import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from .group import Group


def _get_now_utc():
    return datetime.now(timezone.utc)


class ReportEntryModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "report_entries"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    success: Mapped[bool | None] = mapped_column(Boolean, default=False)
    message: Mapped[str] = mapped_column(String, nullable=True)
    exception: Mapped[str] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_get_now_utc)

    report_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("group_reports.id"), nullable=False, index=True)
    report: Mapped["ReportModel"] = orm.relationship("ReportModel", back_populates="entries")

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class ReportModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "group_reports"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_get_now_utc)

    entries: Mapped[list[ReportEntryModel]] = orm.relationship(
        ReportEntryModel, back_populates="report", cascade="all, delete-orphan"
    )

    # Relationships
    group_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="group_reports", single_parent=True)
    model_config = ConfigDict(exclude=["entries"])

    @auto_init()
    def __init__(self, **_) -> None:
        pass
