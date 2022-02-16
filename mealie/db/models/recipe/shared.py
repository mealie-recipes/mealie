from datetime import datetime, timedelta
from uuid import uuid4

import sqlalchemy as sa

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils import GUID, auto_init


def defaut_expires_at_time() -> datetime:
    return datetime.utcnow() + timedelta(days=30)


class RecipeShareTokenModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_share_tokens"
    id = sa.Column(GUID, primary_key=True, default=uuid4)

    group_id = sa.Column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)

    recipe_id = sa.Column(GUID, sa.ForeignKey("recipes.id"), nullable=False)
    recipe = sa.orm.relationship("RecipeModel", back_populates="share_tokens", uselist=False)

    expires_at = sa.Column(sa.DateTime, nullable=False)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
