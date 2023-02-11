from datetime import date, datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped, mapped_column, validates

from mealie.db.models._model_utils.guid import GUID

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import auto_init
from ..users.user_to_favorite import users_to_favorites
from .api_extras import ApiExtras, api_extras
from .assets import RecipeAsset
from .category import recipes_to_categories
from .comment import RecipeComment
from .ingredient import RecipeIngredient
from .instruction import RecipeInstruction
from .note import Note
from .nutrition import Nutrition
from .recipe_timeline import RecipeTimelineEvent
from .settings import RecipeSettings
from .shared import RecipeShareTokenModel
from .tag import recipes_to_tags
from .tool import recipes_to_tools

if TYPE_CHECKING:
    from ..group import Group, GroupMealPlan, ShoppingListItemRecipeReference, ShoppingListRecipeReference
    from ..users import User
    from . import Category, Tag, Tool


class RecipeModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipes"
    __table_args__ = (sa.UniqueConstraint("slug", "group_id", name="recipe_slug_group_id_key"),)

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    slug: Mapped[str | None] = mapped_column(sa.String, index=True)

    # ID Relationships
    group_id: Mapped[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="recipes", foreign_keys=[group_id])

    user_id: Mapped[GUID | None] = mapped_column(GUID, sa.ForeignKey("users.id", use_alter=True), index=True)
    user: Mapped["User"] = orm.relationship("User", uselist=False, foreign_keys=[user_id])

    meal_entries: Mapped["GroupMealPlan"] = orm.relationship(
        "GroupMealPlan", back_populates="recipe", cascade="all, delete-orphan"
    )

    favorited_by: Mapped[list["User"]] = orm.relationship(
        "User", secondary=users_to_favorites, back_populates="favorite_recipes"
    )

    # General Recipe Properties
    name: Mapped[str] = mapped_column(sa.String, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(sa.String)
    image: Mapped[str | None] = mapped_column(sa.String)

    # Time Related Properties
    total_time: Mapped[str | None] = mapped_column(sa.String)
    prep_time: Mapped[str | None] = mapped_column(sa.String)
    perform_time: Mapped[str | None] = mapped_column(sa.String)
    cook_time: Mapped[str | None] = mapped_column(sa.String)

    recipe_yield: Mapped[str | None] = mapped_column(sa.String)
    recipeCuisine: Mapped[str | None] = mapped_column(sa.String)

    assets: Mapped[RecipeAsset] = orm.relationship("RecipeAsset", cascade="all, delete-orphan")
    nutrition: Mapped[Nutrition] = orm.relationship("Nutrition", uselist=False, cascade="all, delete-orphan")
    recipe_category: Mapped[list["Category"]] = orm.relationship(
        "Category", secondary=recipes_to_categories, back_populates="recipes"
    )
    tools: Mapped[list["Tool"]] = orm.relationship("Tool", secondary=recipes_to_tools, back_populates="recipes")

    recipe_ingredient: Mapped[list[RecipeIngredient]] = orm.relationship(
        "RecipeIngredient",
        cascade="all, delete-orphan",
        order_by="RecipeIngredient.position",
        collection_class=ordering_list("position"),
    )
    recipe_instructions: Mapped[list[RecipeInstruction]] = orm.relationship(
        "RecipeInstruction",
        cascade="all, delete-orphan",
        order_by="RecipeInstruction.position",
        collection_class=ordering_list("position"),
    )

    share_tokens: Mapped[list[RecipeShareTokenModel]] = orm.relationship(
        RecipeShareTokenModel, back_populates="recipe", cascade="all, delete, delete-orphan"
    )

    comments: Mapped[list[RecipeComment]] = orm.relationship(
        "RecipeComment", back_populates="recipe", cascade="all, delete, delete-orphan"
    )

    timeline_events: Mapped[list[RecipeTimelineEvent]] = orm.relationship(
        "RecipeTimelineEvent", back_populates="recipe", cascade="all, delete, delete-orphan"
    )

    # Mealie Specific
    settings: Mapped[list["RecipeSettings"]] = orm.relationship(
        "RecipeSettings", uselist=False, cascade="all, delete-orphan"
    )
    tags: Mapped[list["Tag"]] = orm.relationship("Tag", secondary=recipes_to_tags, back_populates="recipes")
    notes: Mapped[list[Note]] = orm.relationship("Note", cascade="all, delete-orphan")
    rating: Mapped[int | None] = mapped_column(sa.Integer)
    org_url: Mapped[str | None] = mapped_column(sa.String)
    extras: Mapped[list[ApiExtras]] = orm.relationship("ApiExtras", cascade="all, delete-orphan")
    is_ocr_recipe: Mapped[bool | None] = mapped_column(sa.Boolean, default=False)

    # Time Stamp Properties
    date_added: Mapped[date | None] = mapped_column(sa.Date, default=date.today)
    date_updated: Mapped[datetime | None] = mapped_column(sa.DateTime)
    last_made: Mapped[datetime | None] = mapped_column(sa.DateTime)

    # Shopping List Refs
    shopping_list_refs: Mapped[list["ShoppingListRecipeReference"]] = orm.relationship(
        "ShoppingListRecipeReference",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    shopping_list_item_refs: Mapped[list["ShoppingListItemRecipeReference"]] = orm.relationship(
        "ShoppingListItemRecipeReference",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )

    class Config:
        get_attr = "slug"
        exclude = {
            "assets",
            "notes",
            "nutrition",
            "recipe_ingredient",
            "recipe_instructions",
            "settings",
            "comments",
            "timeline_events",
        }

    @validates("name")
    def validate_name(self, _, name):
        assert name != ""
        return name

    @api_extras
    @auto_init()
    def __init__(
        self,
        session,
        assets: list | None = None,
        notes: list[dict] | None = None,
        nutrition: dict | None = None,
        recipe_ingredient: list[dict] | None = None,
        recipe_instructions: list[dict] | None = None,
        settings: dict | None = None,
        **_,
    ) -> None:
        self.nutrition = Nutrition(**nutrition) if nutrition else Nutrition()

        if recipe_instructions is not None:
            self.recipe_instructions = [RecipeInstruction(**step, session=session) for step in recipe_instructions]

        if recipe_ingredient is not None:
            self.recipe_ingredient = [RecipeIngredient(**ingr, session=session) for ingr in recipe_ingredient]

        if assets:
            self.assets = [RecipeAsset(**a) for a in assets]

        self.settings = RecipeSettings(**settings) if settings else RecipeSettings()

        if notes:
            self.notes = [Note(**n) for n in notes]

        self.date_updated = datetime.now()
