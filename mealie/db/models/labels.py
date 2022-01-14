from sqlalchemy import Column, ForeignKey, String, orm

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase

from ._model_utils import auto_init
from ._model_utils.guid import GUID


class MultiPurposeLabel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "multi_purpose_labels"
    id = Column(GUID, default=GUID.generate, primary_key=True)
    name = Column(String(255), nullable=False)
    color = Column(String(10), nullable=False, default="")

    group_id = Column(GUID, ForeignKey("groups.id"))
    group = orm.relationship("Group", back_populates="labels")

    shopping_list_items = orm.relationship("ShoppingListItem", back_populates="label")
    foods = orm.relationship("IngredientFoodModel", back_populates="label")

    @auto_init()
    def __init__(self, **_) -> None:
        pass
