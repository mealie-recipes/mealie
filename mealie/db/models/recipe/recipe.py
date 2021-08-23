import datetime
from datetime import date

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import validates

from .._model_base import BaseMixins, SqlAlchemyBase
from .api_extras import ApiExtras
from .assets import RecipeAsset
from .category import Category, recipes2categories
from .ingredient import RecipeIngredient
from .instruction import RecipeInstruction
from .note import Note
from .nutrition import Nutrition
from .settings import RecipeSettings
from .tag import Tag, recipes2tags
from .tool import Tool


class RecipeModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipes"
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
    slug = sa.Column(sa.String, index=True, unique=True)
    settings = orm.relationship("RecipeSettings", uselist=False, cascade="all, delete-orphan")
    tags: list[Tag] = orm.relationship("Tag", secondary=recipes2tags, back_populates="recipes")
    notes: list[Note] = orm.relationship("Note", cascade="all, delete-orphan")
    rating = sa.Column(sa.Integer)
    org_url = sa.Column(sa.String)
    extras: list[ApiExtras] = orm.relationship("ApiExtras", cascade="all, delete-orphan")

    # Time Stamp Properties
    date_added = sa.Column(sa.Date, default=date.today)
    date_updated = sa.Column(sa.DateTime)

    # Favorited By
    favorited_by_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    favorited_by = orm.relationship("User", back_populates="favorite_recipes")

    @validates("name")
    def validate_name(self, key, name):
        assert name != ""
        return name

    def __init__(
        self,
        session,
        name: str = None,
        description: str = None,
        image: str = None,
        recipe_yield: str = None,
        recipe_ingredient: list[str] = None,
        recipe_instructions: list[dict] = None,
        recipeCuisine: str = None,
        total_time: str = None,
        prep_time: str = None,
        cook_time: str = None,
        nutrition: dict = None,
        tools: list[str] = None,
        perform_time: str = None,
        slug: str = None,
        recipe_category: list[str] = None,
        tags: list[str] = None,
        date_added: datetime.date = None,
        notes: list[dict] = None,
        rating: int = None,
        org_url: str = None,
        extras: dict = None,
        assets: list = None,
        settings: dict = None,
        **_
    ) -> None:
        self.name = name
        self.description = description
        self.image = image
        self.recipeCuisine = recipeCuisine

        self.nutrition = Nutrition(**nutrition) if self.nutrition else Nutrition()

        self.tools = [Tool(tool=x) for x in tools] if tools else []

        self.recipe_yield = recipe_yield
        self.recipe_ingredient = [RecipeIngredient(**ingr, session=session) for ingr in recipe_ingredient]
        self.assets = [RecipeAsset(**a) for a in assets]
        self.recipe_instructions = [
            RecipeInstruction(text=instruc.get("text"), title=instruc.get("title"), type=instruc.get("@type", None))
            for instruc in recipe_instructions
        ]
        self.total_time = total_time
        self.prep_time = prep_time
        self.perform_time = perform_time
        self.cook_time = cook_time

        self.recipe_category = [x for x in [Category.get_ref(cat) for cat in recipe_category] if x]

        # Mealie Specific
        self.settings = RecipeSettings(**settings) if settings else RecipeSettings()
        self.tags = [x for x in [Tag.get_ref(tag) for tag in tags] if x]
        self.slug = slug
        self.notes = [Note(**note) for note in notes]
        self.rating = rating
        self.org_url = org_url
        self.extras = [ApiExtras(key=key, value=value) for key, value in extras.items()]

        # Time Stampes
        self.date_added = date_added
        self.date_updated = datetime.datetime.now()
