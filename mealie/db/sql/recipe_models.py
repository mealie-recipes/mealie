import mongoengine
import sqlalchemy as sa
from db.sql.model_base import SqlAlchemyBase


class RecipeSQLModel(SqlAlchemyBase):
    __tablename__ = "recipes"

    name = sa.Column(sa.String, primar_key=True)
    description = sa.Column(sa.String)
    image = sa.Column(sa.String)
    recipeYield = sa.Column(sa.String)
    recipeIngredient = mongoengine.ListField(required=True, default=[])
    recipeInstructions = mongoengine.ListField(requiredd=True, default=[])
    totalTime = sa.Column(sa.String)

    # Mealie Specific
    slug = sa.Column(sa.String)
    categories = mongoengine.ListField(default=[])
    tags = mongoengine.ListField(default=[])
    dateAdded = mongoengine.DateTimeField(binary=True, default=datetime.date.today())
    notes = mongoengine.ListField(default=[])
    rating = sa.Column(sa.Integer)
    orgURL = sa.Column(sa.String)
    extras = mongoengine.DictField(required=False)

    def __repr__(self):
        return f"SQL Entry Recipe {self.name}"
