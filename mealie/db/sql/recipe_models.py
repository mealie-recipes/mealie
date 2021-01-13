from datetime import date

import sqlalchemy as sa
import sqlalchemy.orm as orm
from db.sql.model_base import SqlAlchemyBase


class RecipeModel(SqlAlchemyBase):
    __tablename__ = "recipes"
    # id = mongoengine.UUIDField(primary_key=True)
    name = sa.Column(sa.String)
    description = sa.Column(sa.String)
    image = sa.Column(sa.String)
    recipeYield = sa.Column(sa.String)
    recipeIngredient = orm.relation("RecipeIngredient")
    recipeInstructions = orm.relation("RecipeInstruction")
    totalTime = sa.Column(sa.String)

    # Mealie Specific
    slug = sa.Column(sa.String, primary_key=True, index=True, unique=True)
    categories = orm.relation("Category")
    tags = orm.relation("Tag")
    dateAdded = sa.Column(sa.Date, default=date.today())
    notes = orm.relation("Note")
    rating = sa.Column(sa.Integer)
    orgURL = sa.Column(sa.String)
    extras = orm.relation("ApiExtras")

class ApiExtras(SqlAlchemyBase):
    key: sa.Column(sa.String)
    value: sa.Column(sa.String)

class Category(SqlAlchemyBase):
    name = sa.Column(sa.String, index=True)


class Tag(SqlAlchemyBase):
    name = sa.Column(sa.String, index=True)


class Note(SqlAlchemyBase):
    title = sa.Column(sa.String)
    text = sa.Column(sa.String)


class RecipeIngredient(SqlAlchemyBase):
    ingredient: sa.Column(sa.String)


class RecipeInstruction(SqlAlchemyBase):
    type = sa.Column(sa.String)
    text = sa.Column(sa.String)
