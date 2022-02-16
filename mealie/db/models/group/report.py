from datetime import datetime

from sqlalchemy import Column, ForeignKey, orm
from sqlalchemy.sql.sqltypes import Boolean, DateTime, String

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase

from .._model_utils import auto_init
from .._model_utils.guid import GUID


class ReportEntryModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "report_entries"
    id = Column(GUID, primary_key=True, default=GUID.generate)

    success = Column(Boolean, default=False)
    message = Column(String, nullable=True)
    exception = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    report_id = Column(GUID, ForeignKey("group_reports.id"), nullable=False)
    report = orm.relationship("ReportModel", back_populates="entries")

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class ReportModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "group_reports"
    id = Column(GUID, primary_key=True, default=GUID.generate)

    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    category = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    entries = orm.relationship(ReportEntryModel, back_populates="report", cascade="all, delete-orphan")

    # Relationships
    group_id = Column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group = orm.relationship("Group", back_populates="group_reports", single_parent=True)

    class Config:
        exclude = ["entries"]

    @auto_init()
    def __init__(self, **_) -> None:
        pass
