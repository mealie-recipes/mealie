import datetime
from datetime import date
from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as orm
from db.sql.model_base import BaseMixins, SqlAlchemyBase
from slugify import slugify
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import validates
from utils.logger import logger


class ApiExtras(SqlAlchemyBase):
    __tablename__ = "api_extras"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.id"))
    key_name = sa.Column(sa.String, unique=True)
    value = sa.Column(sa.String)

    def __init__(self, key, value) -> None:
        self.key_name = key
        self.value = value

    def dict(self):
        return {self.key_name: self.value}


recipes2categories = sa.Table(
    "recipes2categories",
    SqlAlchemyBase.metadata,
    sa.Column("recipe_id", sa.Integer, sa.ForeignKey("recipes.id")),
    sa.Column("category_slug", sa.String, sa.ForeignKey("categories.slug")),
)

recipes2tags = sa.Table(
    "recipes2tags",
    SqlAlchemyBase.metadata,
    sa.Column("recipe_id", sa.Integer, sa.ForeignKey("recipes.id")),
    sa.Column("tag_slug", sa.Integer, sa.ForeignKey("tags.slug")),
)


class Category(SqlAlchemyBase):
    __tablename__ = "categories"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, index=True, nullable=False)
    slug = sa.Column(sa.String, index=True, unique=True, nullable=False)
    recipes = orm.relationship(
        "RecipeModel", secondary=recipes2categories, back_populates="categories"
    )

    @validates("name")
    def validate_name(self, key, name):
        assert not name == ""
        return name

    def __init__(self, name) -> None:
        self.name = name.strip()
        self.slug = slugify(name)

    @staticmethod
    def create_if_not_exist(session, name: str = None):
        test_slug = slugify(name)
        try:
            result = session.query(Category).filter(Category.slug == test_slug).one()
            if result:
                logger.info("Category exists, associating recipe")
                return result
            else:
                logger.info("Category doesn't exists, creating tag")
                return Category(name=name)
        except:
            logger.info("Category doesn't exists, creating category")
            return Category(name=name)

    def to_str(self):
        return self.name

    def dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "recipes": [x.dict() for x in self.recipes],
        }


class Tag(SqlAlchemyBase):
    __tablename__ = "tags"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, index=True, nullable=False)
    slug = sa.Column(sa.String, index=True, unique=True, nullable=False)
    recipes = orm.relationship(
        "RecipeModel", secondary=recipes2tags, back_populates="tags"
    )

    @validates("name")
    def validate_name(self, key, name):
        assert not name == ""
        return name

    def to_str(self):
        return self.name

    def __init__(self, name) -> None:
        self.name = name.strip()
        self.slug = slugify(self.name)

    def dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "recipes": [x.dict() for x in self.recipes],
        }

    @staticmethod
    def create_if_not_exist(session, name: str = None):
        test_slug = slugify(name)
        try:
            result = session.query(Tag).filter(Tag.slug == test_slug).first()

            if result:
                logger.info("Tag exists, associating recipe")

                return result
            else:
                logger.info("Tag doesn't exists, creating tag")
                return Tag(name=name)
        except:
            logger.info("Tag doesn't exists, creating tag")
            return Tag(name=name)


class Note(SqlAlchemyBase):
    __tablename__ = "notes"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.id"))
    title = sa.Column(sa.String)
    text = sa.Column(sa.String)

    def __init__(self, title, text) -> None:
        self.title = title
        self.text = text

    def dict(self):
        return {"title": self.title, "text": self.text}


class RecipeIngredient(SqlAlchemyBase):
    __tablename__ = "recipes_ingredients"
    id = sa.Column(sa.Integer, primary_key=True)
    position = sa.Column(sa.Integer)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.id"))
    ingredient = sa.Column(sa.String)

    def update(self, ingredient):
        self.ingredient = ingredient

    def to_str(self):
        return self.ingredient


class RecipeInstruction(SqlAlchemyBase):
    __tablename__ = "recipe_instructions"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.id"))
    position = sa.Column(sa.Integer)
    type = sa.Column(sa.String, default="")
    text = sa.Column(sa.String)

    def dict(self):
        data = {"@type": self.type, "text": self.text}

        return data


class RecipeModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipes"
    # Database Specific
    id = sa.Column(sa.Integer, primary_key=True)

    # General Recipe Properties
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String)
    image = sa.Column(sa.String)
    recipeYield = sa.Column(sa.String)
    recipeIngredient: List[RecipeIngredient] = orm.relationship(
        "RecipeIngredient",
        cascade="all, delete",
        order_by="RecipeIngredient.position",
        collection_class=ordering_list("position"),
    )
    recipeInstructions: List[RecipeInstruction] = orm.relationship(
        "RecipeInstruction",
        cascade="all, delete",
        order_by="RecipeInstruction.position",
        collection_class=ordering_list("position"),
    )

    # How to Properties
    totalTime = sa.Column(sa.String)
    prepTime = sa.Column(sa.String)
    performTime = sa.Column(sa.String)

    # Mealie Specific
    slug = sa.Column(sa.String, index=True, unique=True)
    categories: List = orm.relationship(
        "Category", secondary=recipes2categories, back_populates="recipes"
    )
    tags: List[Tag] = orm.relationship(
        "Tag", secondary=recipes2tags, back_populates="recipes"
    )
    dateAdded = sa.Column(sa.Date, default=date.today)
    notes: List[Note] = orm.relationship("Note", cascade="all, delete")
    rating = sa.Column(sa.Integer)
    orgURL = sa.Column(sa.String)
    extras: List[ApiExtras] = orm.relationship("ApiExtras", cascade="all, delete")

    @validates("name")
    def validate_name(self, key, name):
        assert not name == ""
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
        totalTime: str = None,
        prepTime: str = None,
        performTime: str = None,
        slug: str = None,
        categories: List[str] = None,
        tags: List[str] = None,
        dateAdded: datetime.date = None,
        notes: List[dict] = None,
        rating: int = None,
        orgURL: str = None,
        extras: dict = None,
    ) -> None:
        self.name = name
        self.description = description
        self.image = image
        self.recipeYield = recipeYield
        self.recipeIngredient = [
            RecipeIngredient(ingredient=ingr) for ingr in recipeIngredient
        ]
        self.recipeInstructions = [
            RecipeInstruction(text=instruc.get("text"), type=instruc.get("@type", None))
            for instruc in recipeInstructions
        ]
        self.totalTime = totalTime
        self.prepTime = prepTime
        self.performTime = performTime

        # Mealie Specific
        self.slug = slug
        self.categories = [
            Category.create_if_not_exist(session=session, name=cat)
            for cat in categories
        ]

        self.tags = [Tag.create_if_not_exist(session=session, name=tag) for tag in tags]

        self.dateAdded = dateAdded
        self.notes = [Note(**note) for note in notes]
        self.rating = rating
        self.orgURL = orgURL
        self.extras = [ApiExtras(key=key, value=value) for key, value in extras.items()]

    def update(
        self,
        session,
        name: str = None,
        description: str = None,
        image: str = None,
        recipeYield: str = None,
        recipeIngredient: List[str] = None,
        recipeInstructions: List[dict] = None,
        totalTime: str = None,
        prepTime: str = None,
        performTime: str = None,
        slug: str = None,
        categories: List[str] = None,
        tags: List[str] = None,
        dateAdded: datetime.date = None,
        notes: List[dict] = None,
        rating: int = None,
        orgURL: str = None,
        extras: dict = None,
    ):
        """Updated a database entry by removing nested rows and rebuilds the row through the __init__ functions"""
        list_of_tables = [RecipeIngredient, RecipeInstruction, ApiExtras]
        RecipeModel._sql_remove_list(session, list_of_tables, self.id)

        self.__init__(
            session=session,
            name=name,
            description=description,
            image=image,
            recipeYield=recipeYield,
            recipeIngredient=recipeIngredient,
            recipeInstructions=recipeInstructions,
            totalTime=totalTime,
            prepTime=prepTime,
            performTime=performTime,
            slug=slug,
            categories=categories,
            tags=tags,
            dateAdded=dateAdded,
            notes=notes,
            rating=rating,
            orgURL=orgURL,
            extras=extras,
        )

    def dict(self):
        data = {
            "name": self.name,
            "description": self.description,
            "image": self.image,
            "recipeYield": self.recipeYield,
            "recipeIngredient": [x.to_str() for x in self.recipeIngredient],
            "recipeInstructions": [x.dict() for x in self.recipeInstructions],
            "totalTime": self.totalTime,
            "prepTime": self.prepTime,
            "performTime": self.performTime,
            # Mealie
            "slug": self.slug,
            "categories": [x.to_str() for x in self.categories],
            "tags": [x.to_str() for x in self.tags],
            "dateAdded": self.dateAdded,
            "notes": [x.dict() for x in self.notes],
            "rating": self.rating,
            "orgURL": self.orgURL,
            "extras": RecipeModel._flatten_dict(self.extras),
        }

        return data
