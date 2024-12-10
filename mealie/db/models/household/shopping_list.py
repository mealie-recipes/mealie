from contextvars import ContextVar
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from pydantic import ConfigDict
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, UniqueConstraint, event, orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models.labels import MultiPurposeLabel
from mealie.db.models.recipe.api_extras import ShoppingListExtras, ShoppingListItemExtras, api_extras

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID
from ..recipe.ingredient import IngredientFoodModel, IngredientUnitModel

if TYPE_CHECKING:
    from ..group import Group
    from ..recipe import RecipeModel
    from ..users import User
    from .household import Household


class ShoppingListItemRecipeReference(BaseMixins, SqlAlchemyBase):
    __tablename__ = "shopping_list_item_recipe_reference"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    shopping_list_item: Mapped["ShoppingListItem"] = orm.relationship(
        "ShoppingListItem", back_populates="recipe_references"
    )
    shopping_list_item_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("shopping_list_items.id"), primary_key=True)

    recipe_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("recipes.id"), index=True)
    recipe: Mapped[Optional["RecipeModel"]] = orm.relationship("RecipeModel", back_populates="shopping_list_item_refs")
    recipe_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    recipe_scale: Mapped[float] = mapped_column(Float, default=1)
    recipe_note: Mapped[str | None] = mapped_column(String)

    group_id: AssociationProxy[GUID] = association_proxy("shopping_list_item", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("shopping_list_item", "household_id")

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class ShoppingListItem(SqlAlchemyBase, BaseMixins):
    __tablename__ = "shopping_list_items"

    # Id's
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    shopping_list: Mapped["ShoppingList"] = orm.relationship("ShoppingList", back_populates="list_items")
    shopping_list_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("shopping_lists.id"), index=True)

    group_id: AssociationProxy[GUID] = association_proxy("shopping_list", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("shopping_list", "household_id")

    # Meta
    is_ingredient: Mapped[bool | None] = mapped_column(Boolean, default=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    checked: Mapped[bool | None] = mapped_column(Boolean, default=False)

    quantity: Mapped[float | None] = mapped_column(Float, default=1)
    note: Mapped[str | None] = mapped_column(String)

    is_food: Mapped[bool | None] = mapped_column(Boolean, default=False)
    extras: Mapped[list[ShoppingListItemExtras]] = orm.relationship(
        "ShoppingListItemExtras", cascade="all, delete-orphan"
    )

    # Scaling Items
    unit_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("ingredient_units.id"))
    unit: Mapped[IngredientUnitModel | None] = orm.relationship(IngredientUnitModel, uselist=False)

    food_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("ingredient_foods.id"))
    food: Mapped[IngredientFoodModel | None] = orm.relationship(IngredientFoodModel, uselist=False)

    label_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("multi_purpose_labels.id"))
    label: Mapped[MultiPurposeLabel | None] = orm.relationship(
        MultiPurposeLabel, uselist=False, back_populates="shopping_list_items"
    )

    # Recipe Reference
    recipe_references: Mapped[list[ShoppingListItemRecipeReference]] = orm.relationship(
        ShoppingListItemRecipeReference, cascade="all, delete, delete-orphan"
    )
    model_config = ConfigDict(exclude={"label", "food", "unit"})

    @api_extras
    @auto_init()
    def __init__(self, **_) -> None:
        pass


class ShoppingListRecipeReference(BaseMixins, SqlAlchemyBase):
    __tablename__ = "shopping_list_recipe_reference"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    shopping_list: Mapped["ShoppingList"] = orm.relationship("ShoppingList", back_populates="recipe_references")
    shopping_list_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("shopping_lists.id"), primary_key=True)
    group_id: AssociationProxy[GUID] = association_proxy("shopping_list", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("shopping_list", "household_id")

    recipe_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("recipes.id"), index=True)
    recipe: Mapped[Optional["RecipeModel"]] = orm.relationship(
        "RecipeModel", uselist=False, back_populates="shopping_list_refs"
    )

    recipe_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    model_config = ConfigDict(exclude={"id", "recipe"})

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class ShoppingListMultiPurposeLabel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "shopping_lists_multi_purpose_labels"
    __table_args__ = (UniqueConstraint("shopping_list_id", "label_id", name="shopping_list_id_label_id_key"),)
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    shopping_list_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("shopping_lists.id"), primary_key=True)
    shopping_list: Mapped["ShoppingList"] = orm.relationship("ShoppingList", back_populates="label_settings")

    label_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("multi_purpose_labels.id"), primary_key=True)
    label: Mapped["MultiPurposeLabel"] = orm.relationship(
        "MultiPurposeLabel", back_populates="shopping_lists_label_settings"
    )

    group_id: AssociationProxy[GUID] = association_proxy("shopping_list", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("shopping_list", "household_id")

    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    model_config = ConfigDict(exclude={"label"})

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class ShoppingList(SqlAlchemyBase, BaseMixins):
    __tablename__ = "shopping_lists"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    group_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="shopping_lists")
    household_id: AssociationProxy[GUID] = association_proxy("user", "household_id")
    household: AssociationProxy["Household"] = association_proxy("user", "household")
    user_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = orm.relationship("User", back_populates="shopping_lists")

    name: Mapped[str | None] = mapped_column(String)
    list_items: Mapped[list[ShoppingListItem]] = orm.relationship(
        ShoppingListItem,
        cascade="all, delete, delete-orphan",
        order_by="ShoppingListItem.position",
        collection_class=ordering_list("position"),
    )

    recipe_references: Mapped[list[ShoppingListRecipeReference]] = orm.relationship(
        ShoppingListRecipeReference, cascade="all, delete, delete-orphan"
    )
    label_settings: Mapped[list["ShoppingListMultiPurposeLabel"]] = orm.relationship(
        ShoppingListMultiPurposeLabel,
        cascade="all, delete, delete-orphan",
        order_by="ShoppingListMultiPurposeLabel.position",
        collection_class=ordering_list("position"),
    )
    extras: Mapped[list[ShoppingListExtras]] = orm.relationship("ShoppingListExtras", cascade="all, delete-orphan")
    model_config = ConfigDict(exclude={"id", "list_items"})

    @api_extras
    @auto_init()
    def __init__(self, **_) -> None:
        pass


class SessionBuffer:
    def __init__(self) -> None:
        self.shopping_list_ids: set[GUID] = set()

    def add(self, shopping_list_id: GUID) -> None:
        self.shopping_list_ids.add(shopping_list_id)

    def pop(self) -> GUID | None:
        try:
            return self.shopping_list_ids.pop()
        except KeyError:
            return None

    def clear(self) -> None:
        self.shopping_list_ids.clear()


session_buffer_context = ContextVar("session_buffer", default=SessionBuffer())  # noqa: B039


@event.listens_for(ShoppingListItem, "after_insert")
@event.listens_for(ShoppingListItem, "after_update")
@event.listens_for(ShoppingListItem, "after_delete")
def buffer_shopping_list_updates(_, connection, target: ShoppingListItem):
    """Adds the shopping list id to the session buffer so its `updated_at` property can be updated later"""

    session_buffer = session_buffer_context.get()
    session_buffer.add(target.shopping_list_id)


@event.listens_for(orm.Session, "after_flush")
def update_shopping_lists(session: orm.Session, _):
    """Pulls all pending shopping list updates from the buffer and updates their `updated_at` property"""

    session_buffer = session_buffer_context.get()
    if not session_buffer.shopping_list_ids:
        return

    local_session = orm.Session(bind=session.connection())
    try:
        local_session.begin()
        while True:
            shopping_list_id = session_buffer.pop()
            if not shopping_list_id:
                break

            shopping_list = local_session.query(ShoppingList).filter(ShoppingList.id == shopping_list_id).first()
            if not shopping_list:
                continue

            shopping_list.updated_at = datetime.now(UTC)
        local_session.commit()
    except Exception:
        local_session.rollback()
        raise
