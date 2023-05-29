from datetime import date, datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy import event
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped, mapped_column, validates
from text_unidecode import unidecode

from mealie.db.models._model_utils.guid import GUID

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import auto_init
from ..users.user_to_favorite import users_to_favorites
from .api_extras import ApiExtras, api_extras
from .assets import RecipeAsset
from .category import recipes_to_categories
from .comment import RecipeComment
from .ingredient import RecipeIngredientModel
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
    __table_args__: tuple[sa.UniqueConstraint, ...] = (
        sa.UniqueConstraint("slug", "group_id", name="recipe_slug_group_id_key"),
    )

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
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
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

    recipe_ingredient: Mapped[list[RecipeIngredientModel]] = orm.relationship(
        "RecipeIngredientModel",
        cascade="all, delete-orphan",
        order_by="RecipeIngredientModel.position",
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

    # Automatically updated by sqlalchemy event, do not write to this manually
    name_normalized: Mapped[str] = mapped_column(sa.String, nullable=False, index=True)
    description_normalized: Mapped[str | None] = mapped_column(sa.String, index=True)

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
        name: str | None = None,
        description: str | None = None,
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
            self.recipe_ingredient = [RecipeIngredientModel(**ingr, session=session) for ingr in recipe_ingredient]

        if assets:
            self.assets = [RecipeAsset(**a) for a in assets]

        self.settings = RecipeSettings(**settings) if settings else RecipeSettings()

        if notes:
            self.notes = [Note(**n) for n in notes]

        self.date_updated = datetime.now()

        # SQLAlchemy events do not seem to register things that are set during auto_init
        if name is not None:
            self.name_normalized = unidecode(name).lower().strip()

        if description is not None:
            self.description_normalized = unidecode(description).lower().strip()

        tableargs = [  # base set of indices
            sa.UniqueConstraint("slug", "group_id", name="recipe_slug_group_id_key"),
            sa.Index(
                "ix_recipes_name_normalized",
                "name_normalized",
                unique=False,
            ),
            sa.Index(
                "ix_recipes_description_normalized",
                "description_normalized",
                unique=False,
            ),
        ]

        if session.get_bind().name == "postgresql":
            tableargs.extend(
                [
                    sa.Index(
                        "ix_recipes_name_normalized_gin",
                        "name_normalized",
                        unique=False,
                        postgresql_using="gin",
                        postgresql_ops={
                            "name_normalized": "gin_trgm_ops",
                        },
                    ),
                    sa.Index(
                        "ix_recipes_description_normalized_gin",
                        "description_normalized",
                        unique=False,
                        postgresql_using="gin",
                        postgresql_ops={
                            "description_normalized": "gin_trgm_ops",
                        },
                    ),
                ]
            )
        # add indices
        self.__table_args__ = tuple(tableargs)


@event.listens_for(RecipeModel.name, "set")
def receive_name(target: RecipeModel, value: str, oldvalue, initiator):
    target.name_normalized = unidecode(value).lower().strip()


@event.listens_for(RecipeModel.description, "set")
def receive_description(target: RecipeModel, value: str, oldvalue, initiator):
    if value is not None:
        target.description_normalized = unidecode(value).lower().strip()
    else:
        target.description_normalized = None
