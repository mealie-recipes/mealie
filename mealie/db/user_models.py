import datetime

import mongoengine

class User(mongoengine.Document):
    username: mongoengine.EmailField()
    # password: mongoengine.ReferenceField