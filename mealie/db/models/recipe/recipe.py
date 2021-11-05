import datetime
from datetime import date

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import validates

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import auto_init
from ..users import users_to_favorites
from .api_extras import ApiExtras
from .assets import RecipeAsset
from .category import recipes2categories
from .ingredient import RecipeIngredient
from .instruction import RecipeInstruction
from .note import Note
from .nutrition import Nutrition
from .settings import RecipeSettings
from .tag import Tag, recipes2tags
from .tool import Tool


class RecipeModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipes"
    __table_args__ = (sa.UniqueConstraint("slug", "group_id", name="recipe_slug_group_id_key"),)

    slug = sa.Column(sa.String, index=True)

    # ID Relationships
    group_id = sa.Column(sa.Integer, sa.ForeignKey("groups.id"))
    group = orm.relationship("Group", back_populates="recipes", foreign_keys=[group_id])

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    user = orm.relationship("User", uselist=False, foreign_keys=[user_id])

    meal_entries = orm.relationship("GroupMealPlan", back_populates="recipe")

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

    tools: list[Tool] = orm.relationship("Tool", cascade="all, delete-orphan")
    assets: list[RecipeAsset] = orm.relationship("RecipeAsset", cascade="all, delete-orphan")
    nutrition: Nutrition = orm.relationship("Nutrition", uselist=False, cascade="all, delete-orphan")
    recipe_category: list = orm.relationship("Category", secondary=recipes2categories, back_populates="recipes")

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

    comments: list = orm.relationship("RecipeComment", back_populates="recipe", cascade="all, delete, delete-orphan")

    # Mealie Specific
    settings = orm.relationship("RecipeSettings", uselist=False, cascade="all, delete-orphan")
    tags: list[Tag] = orm.relationship("Tag", secondary=recipes2tags, back_populates="recipes")
    notes: list[Note] = orm.relationship("Note", cascade="all, delete-orphan")
    rating = sa.Column(sa.Integer)
    org_url = sa.Column(sa.String)
    extras: list[ApiExtras] = orm.relationship("ApiExtras", cascade="all, delete-orphan")

    # Time Stamp Properties
    date_added = sa.Column(sa.Date, default=date.today)
    date_updated = sa.Column(sa.DateTime)

    class Config:
        get_attr = "slug"
        exclude = {
            "assets",
            "extras",
            "notes",
            "nutrition",
            "recipe_ingredient",
            "settings",
            "tools",
        }

    @validates("name")
    def validate_name(self, key, name):
        assert name != ""
        return name

    @auto_init()
    def __init__(
        self,
        session,
        assets: list = None,
        extras: dict = None,
        notes: list[dict] = None,
        nutrition: dict = None,
        recipe_ingredient: list[str] = None,
        settings: dict = None,
        tools: list[str] = None,
        **_,
    ) -> None:
        self.nutrition = Nutrition(**nutrition) if nutrition else Nutrition()
        self.tools = [Tool(tool=x) for x in tools] if tools else []
        self.recipe_ingredient = [RecipeIngredient(**ingr, session=session) for ingr in recipe_ingredient]
        self.assets = [RecipeAsset(**a) for a in assets]
        # self.recipe_instructions = [
        #     RecipeInstruction(text=instruc.get("text"), title=instruc.get("title"), type=instruc.get("@type", None))
        #     for instruc in recipe_instructions
        # ]

        # Mealie Specific
        self.settings = RecipeSettings(**settings) if settings else RecipeSettings()
        self.notes = [Note(**note) for note in notes]
        self.extras = [ApiExtras(key=key, value=value) for key, value in extras.items()]

        # Time Stampes
        self.date_updated = datetime.datetime.now()
