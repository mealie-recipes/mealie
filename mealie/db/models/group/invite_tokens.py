from sqlalchemy import Column, ForeignKey, Integer, String, orm

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import auto_init, guid


class GroupInviteToken(SqlAlchemyBase, BaseMixins):
    __tablename__ = "invite_tokens"
    token = Column(String, index=True, nullable=False, unique=True)
    uses_left = Column(Integer, nullable=False, default=1)

    group_id = Column(guid.GUID, ForeignKey("groups.id"))
    group = orm.relationship("Group", back_populates="invite_tokens")

    @auto_init()
    def __init__(self, **_):
        pass
