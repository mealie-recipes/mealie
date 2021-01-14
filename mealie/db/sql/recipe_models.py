from datetime import date
from typing import List

import sqlalchemy as sa
import sqlalchemy.orm as orm
from db.sql.model_base import SqlAlchemyBase


class ApiExtras(SqlAlchemyBase):
    __tablename__ = "api_extras"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.slug"))
    key: sa.Column(sa.String, primary_key=True)
    value: sa.Column(sa.String)

    def dict(self):
        return {self.key: self.value}


class Category(SqlAlchemyBase):
    __tablename__ = "categories"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.slug"))
    name = sa.Column(sa.String, index=True)

    def dict(self):
        return self.name


class Tag(SqlAlchemyBase):
    __tablename__ = "tags"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.slug"))
    name = sa.Column(sa.String, index=True)

    def dict(self):
        return self.name


class Note(SqlAlchemyBase):
    __tablename__ = "notes"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.slug"))
    title = sa.Column(sa.String)
    text = sa.Column(sa.String)

    def dict(self):
        return {"title": self.title, "text": self.text}


class RecipeIngredient(SqlAlchemyBase):
    __tablename__ = "recipes_ingredients"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.slug"))
    ingredient = sa.Column(sa.String)

    def dict(self):
        return self.ingredient


class RecipeInstruction(SqlAlchemyBase):
    __tablename__ = "recipe_instructions"
    id = sa.Column(sa.Integer, primary_key=True)
    parent_id = sa.Column(sa.String, sa.ForeignKey("recipes.slug"))
    type = sa.Column(sa.String)
    text = sa.Column(sa.String)

    def dict(self):
        data = {"@type": self.type, "text": self.text}

        return data


class RecipeModel(SqlAlchemyBase):
    __tablename__ = "recipes"
    name = sa.Column(sa.String)
    description = sa.Column(sa.String)
    image = sa.Column(sa.String)
    recipeYield = sa.Column(sa.String)
    recipeIngredient: List[RecipeIngredient] = orm.relation("RecipeIngredient")
    recipeInstructions: List[RecipeInstruction] = orm.relation("RecipeInstruction")
    totalTime = sa.Column(sa.String)

    # Mealie Specific
    slug = sa.Column(sa.String, primary_key=True, index=True, unique=True)
    categories: List[Category] = orm.relation("Category")
    tags: List[Tag] = orm.relation("Tag")
    dateAdded = sa.Column(sa.Date, default=date.today)
    notes: List[Note] = orm.relation("Note")
    rating = sa.Column(sa.Integer)
    orgURL = sa.Column(sa.String)
    extras: List[ApiExtras] = orm.relation("ApiExtras")

    @staticmethod
    def _flatten_dict(list_of_dict: List[dict]):
        finalMap = {}
        for d in list_of_dict:
            finalMap.update(d)

        return finalMap

    def dict(self):
        data = {
            "name": self.name,
            "description": self.description,
            "image": self.image,
            "recipeYield": self.recipeYield,
            "recipeIngredient": [x.dict() for x in self.recipeIngredient],
            "recipeInstructions": [x.dict() for x in self.recipeInstructions],
            "totalTime": self.totalTime,
            # Mealie
            "slug": self.slug,
            "categories": [x.dict() for x in self.categories],
            "tags": [x.dict() for x in self.tags],
            "dateAdded": self.dateAdded,
            "notes": [x.dict() for x in self.notes],
            "rating": self.rating,
            "orgURL": self.orgURL,
            "extras": RecipeModel._flatten_dict(self.extras),
        }

        return data
