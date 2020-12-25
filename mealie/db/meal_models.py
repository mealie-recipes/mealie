import uuid

import mongoengine


class MealDocument(mongoengine.EmbeddedDocument):
    slug = mongoengine.StringField()
    name = mongoengine.StringField()
    date = mongoengine.DateField()
    dateText = mongoengine.StringField()
    image = mongoengine.StringField()
    description = mongoengine.StringField()


class MealPlanDocument(mongoengine.Document):
    uid = mongoengine.UUIDField(default=uuid.uuid1)
    startDate = mongoengine.DateField(required=True)
    endDate = mongoengine.DateField(required=True)
    meals = mongoengine.ListField(required=True)

    meta = {
        "db_alias": "core",
        "collection": "meals",
    }
