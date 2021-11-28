import sqlalchemy as sa
import sqlalchemy.orm as orm

from mealie.db.models._model_utils.guid import GUID

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import auto_init


class GroupPreferencesModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "group_preferences"
    group_id = sa.Column(GUID, sa.ForeignKey("groups.id"))
    group = orm.relationship("Group", back_populates="preferences")

    private_group: bool = sa.Column(sa.Boolean, default=True)
    first_day_of_week = sa.Column(sa.Integer, default=0)

    # Recipe Defaults
    recipe_public: bool = sa.Column(sa.Boolean, default=True)
    recipe_show_nutrition: bool = sa.Column(sa.Boolean, default=False)
    recipe_show_assets: bool = sa.Column(sa.Boolean, default=False)
    recipe_landscape_view: bool = sa.Column(sa.Boolean, default=False)
    recipe_disable_comments: bool = sa.Column(sa.Boolean, default=False)
    recipe_disable_amount: bool = sa.Column(sa.Boolean, default=False)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
