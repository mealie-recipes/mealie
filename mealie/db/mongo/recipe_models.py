import datetime

import mongoengine


class RecipeDocument(mongoengine.Document):
    # Standard Schema
    # id = mongoengine.UUIDField(primary_key=True)
    name = mongoengine.StringField(required=True)
    description = mongoengine.StringField(required=True)
    image = mongoengine.StringField(required=False)
    recipeYield = mongoengine.StringField(required=True, default="")
    recipeIngredient = mongoengine.ListField(required=True, default=[])
    recipeInstructions = mongoengine.ListField(requiredd=True, default=[])
    totalTime = mongoengine.StringField(required=False)
    prepTime = mongoengine.StringField(required=False)
    performTime = mongoengine.StringField(required=False)

    # Mealie Specific
    slug = mongoengine.StringField(required=True, unique=True)
    categories = mongoengine.ListField(default=[])
    tags = mongoengine.ListField(default=[])
    dateAdded = mongoengine.DateTimeField(binary=True, default=datetime.date.today)
    notes = mongoengine.ListField(default=[])
    rating = mongoengine.IntField(required=True, default=0)
    orgURL = mongoengine.URLField(required=False)
    extras = mongoengine.DictField(required=False)

    meta = {
        "db_alias": "core",
        "collection": "recipes",
    }


if __name__ == "__main__":
    pass
