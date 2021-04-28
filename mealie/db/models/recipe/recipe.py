import datetime
from datetime import date
from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as orm
from mealie.db.models.model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models.recipe.api_extras import ApiExtras
from mealie.db.models.recipe.assets import RecipeAsset
from mealie.db.models.recipe.category import Category, recipes2categories
from mealie.db.models.recipe.ingredient import RecipeIngredient
from mealie.db.models.recipe.instruction import RecipeInstruction
from mealie.db.models.recipe.note import Note
from mealie.db.models.recipe.nutrition import Nutrition
from mealie.db.models.recipe.tag import Tag, recipes2tags
from mealie.db.models.recipe.tool import Tool
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import validates


class RecipeModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipes"
    # Database Specific
    id = sa.Column(sa.Integer, primary_key=True)

    # General Recipe Properties
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String)
    image = sa.Column(sa.String)
    totalTime = sa.Column(sa.String)
    prepTime = sa.Column(sa.String)
    performTime = sa.Column(sa.String)
    cookTime = sa.Column(sa.String)
    recipeYield = sa.Column(sa.String)
    recipeCuisine = sa.Column(sa.String)
    tools: List[Tool] = orm.relationship("Tool", cascade="all, delete-orphan")
    nutrition: Nutrition = orm.relationship("Nutrition", uselist=False, cascade="all, delete-orphan")
    recipeCategory: List = orm.relationship("Category", secondary=recipes2categories, back_populates="recipes")

    recipeIngredient: List[RecipeIngredient] = orm.relationship(
        "RecipeIngredient",
        cascade="all, delete-orphan",
        order_by="RecipeIngredient.position",
        collection_class=ordering_list("position"),
    )
    recipeInstructions: List[RecipeInstruction] = orm.relationship(
        "RecipeInstruction",
        cascade="all, delete-orphan",
        order_by="RecipeInstruction.position",
        collection_class=ordering_list("position"),
    )

    # Mealie Specific
    slug = sa.Column(sa.String, index=True, unique=True)
    tags: List[Tag] = orm.relationship("Tag", secondary=recipes2tags, back_populates="recipes")
    dateAdded = sa.Column(sa.Date, default=date.today)
    notes: List[Note] = orm.relationship("Note", cascade="all, delete-orphan")
    rating = sa.Column(sa.Integer)
    orgURL = sa.Column(sa.String)
    extras: List[ApiExtras] = orm.relationship("ApiExtras", cascade="all, delete-orphan")

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
        recipeYield: str = None,
        recipeIngredient: List[str] = None,
        recipeInstructions: List[dict] = None,
        recipeCuisine: str = None,
        totalTime: str = None,
        prepTime: str = None,
        nutrition: dict = None,
        tools: list[str] = [],
        performTime: str = None,
        slug: str = None,
        recipeCategory: List[str] = None,
        tags: List[str] = None,
        dateAdded: datetime.date = None,
        notes: List[dict] = None,
        rating: int = None,
        orgURL: str = None,
        extras: dict = None,
        assets: list = None,
        *args,
        **kwargs
    ) -> None:
        self.name = name
        self.description = description
        self.image = image
        self.recipeCuisine = recipeCuisine

        self.nutrition = Nutrition(**nutrition) if self.nutrition else Nutrition()
        self.tools = [Tool(tool=x) for x in tools] if tools else []

        self.recipeYield = recipeYield
        self.recipeIngredient = [RecipeIngredient(ingredient=ingr) for ingr in recipeIngredient]
        self.assets = [RecipeAsset(name=a.get("name"), icon=a.get("icon")) for a in assets]
        self.recipeInstructions = [
            RecipeInstruction(text=instruc.get("text"), title=instruc.get("title"), type=instruc.get("@type", None))
            for instruc in recipeInstructions
        ]
        self.totalTime = totalTime
        self.prepTime = prepTime
        self.performTime = performTime

        self.recipeCategory = [Category.create_if_not_exist(session=session, name=cat) for cat in recipeCategory]

        # Mealie Specific
        self.tags = [Tag.create_if_not_exist(session=session, name=tag) for tag in tags]
        self.slug = slug
        self.dateAdded = dateAdded
        self.notes = [Note(**note) for note in notes]
        self.rating = rating
        self.orgURL = orgURL
        self.extras = [ApiExtras(key=key, value=value) for key, value in extras.items()]

    def update(self, *args, **kwargs):
        """Updated a database entry by removing nested rows and rebuilds the row through the __init__ functions"""

        self.__init__(*args, **kwargs)
