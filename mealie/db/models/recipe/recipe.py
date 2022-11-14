import datetime

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import validates

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


class RecipeModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipes"
    __table_args__ = (sa.UniqueConstraint("slug", "group_id", name="recipe_slug_group_id_key"),)

    id = sa.Column(GUID, primary_key=True, default=GUID.generate)
    slug = sa.Column(sa.String, index=True)

    # ID Relationships
    group_id = sa.Column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    group = orm.relationship("Group", back_populates="recipes", foreign_keys=[group_id])

    user_id = sa.Column(GUID, sa.ForeignKey("users.id", use_alter=True), index=True)
    user = orm.relationship("User", uselist=False, foreign_keys=[user_id])

    meal_entries = orm.relationship("GroupMealPlan", back_populates="recipe", cascade="all, delete-orphan")

    favorited_by = orm.relationship("User", secondary=users_to_favorites, back_populates="favorite_recipes")

    # General Recipe Properties
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String)
    image = sa.Column(sa.String)

    # Time Related Properties
    total_time = sa.Column(sa.String)
    prep_time = sa.Column(sa.String)
    perform_time = sa.Column(sa.String)
    cook_time = sa.Column(sa.String)

    recipe_yield = sa.Column(sa.String)
    recipeCuisine = sa.Column(sa.String)

    assets = orm.relationship("RecipeAsset", cascade="all, delete-orphan")
    nutrition: Nutrition = orm.relationship("Nutrition", uselist=False, cascade="all, delete-orphan")
    recipe_category = orm.relationship("Category", secondary=recipes_to_categories, back_populates="recipes")
    tools = orm.relationship("Tool", secondary=recipes_to_tools, back_populates="recipes")

    recipe_ingredient: list[RecipeIngredient] = orm.relationship(
        "RecipeIngredient",
        cascade="all, delete-orphan",
        order_by="RecipeIngredient.position",
        collection_class=ordering_list("position"),
    )
    recipe_instructions: list[RecipeInstruction] = orm.relationship(
        "RecipeInstruction",
        cascade="all, delete-orphan",
        order_by="RecipeInstruction.position",
        collection_class=ordering_list("position"),
    )

    share_tokens = orm.relationship(
        RecipeShareTokenModel, back_populates="recipe", cascade="all, delete, delete-orphan"
    )

    comments: list[RecipeComment] = orm.relationship(
        "RecipeComment", back_populates="recipe", cascade="all, delete, delete-orphan"
    )

    timeline_events: list[RecipeTimelineEvent] = orm.relationship(
        "RecipeTimelineEvent", back_populates="recipe", cascade="all, delete, delete-orphan"
    )

    # Mealie Specific
    settings = orm.relationship("RecipeSettings", uselist=False, cascade="all, delete-orphan")
    tags = orm.relationship("Tag", secondary=recipes_to_tags, back_populates="recipes")
    notes: list[Note] = orm.relationship("Note", cascade="all, delete-orphan")
    rating = sa.Column(sa.Integer)
    org_url = sa.Column(sa.String)
    extras: list[ApiExtras] = orm.relationship("ApiExtras", cascade="all, delete-orphan")
    is_ocr_recipe = sa.Column(sa.Boolean, default=False)

    # Time Stamp Properties
    date_added = sa.Column(sa.Date, default=datetime.date.today)
    date_updated = sa.Column(sa.DateTime)
    last_made = sa.Column(sa.DateTime)

    # Shopping List Refs
    shopping_list_refs = orm.relationship(
        "ShoppingListRecipeReference",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    shopping_list_item_refs = orm.relationship(
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
        assets: list = None,
        notes: list[dict] = None,
        nutrition: dict = None,
        recipe_ingredient: list[dict] = None,
        recipe_instructions: list[dict] = None,
        settings: dict = None,
        **_,
    ) -> None:
        self.nutrition = Nutrition(**nutrition) if nutrition else Nutrition()

        if recipe_instructions:
            self.recipe_instructions = [RecipeInstruction(**step, session=session) for step in recipe_instructions]

        if recipe_ingredient:
            self.recipe_ingredient = [RecipeIngredient(**ingr, session=session) for ingr in recipe_ingredient]

        if assets:
            self.assets = [RecipeAsset(**a) for a in assets]

        self.settings = RecipeSettings(**settings) if settings else RecipeSettings()

        if notes:
            self.notes = [Note(**n) for n in notes]

        self.date_updated = datetime.datetime.now()
