from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint, orm
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase

from ._model_utils.auto_init import auto_init
from ._model_utils.guid import GUID

if TYPE_CHECKING:
    from .group.group import Group
    from .household.shopping_list import ShoppingListItem, ShoppingListMultiPurposeLabel
    from .recipe import IngredientFoodModel


class MultiPurposeLabel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "multi_purpose_labels"
    __table_args__ = (UniqueConstraint("name", "group_id", name="multi_purpose_labels_name_group_id_key"),)

    id: Mapped[GUID] = mapped_column(GUID, default=GUID.generate, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    color: Mapped[str] = mapped_column(String(10), nullable=False, default="")

    group_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="labels")

    shopping_list_items: Mapped["ShoppingListItem"] = orm.relationship("ShoppingListItem", back_populates="label")
    foods: Mapped["IngredientFoodModel"] = orm.relationship("IngredientFoodModel", back_populates="label")
    shopping_lists_label_settings: Mapped[list["ShoppingListMultiPurposeLabel"]] = orm.relationship(
        "ShoppingListMultiPurposeLabel", back_populates="label", cascade="all, delete, delete-orphan"
    )

    @auto_init()
    def __init__(self, **_) -> None:
        pass
