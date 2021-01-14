import json

import mongoengine
from settings import USE_MONGO, USE_SQL

from db.sql.db_session import create_session
from db.sql.model_base import SqlAlchemyBase


class BaseDocument:
    def __init__(self) -> None:
        self.primary_key: str
        self.store: str
        self.document: mongoengine.Document
        self.sql_model: SqlAlchemyBase

    @staticmethod  # TODO: Probably Put a version in each class to speed up reads?
    def _unpack_mongo(document) -> dict:
        document = json.loads(document.to_json())
        del document["_id"]

        # Recipe Cleanup
        try:
            document["dateAdded"] = document["dateAdded"]["$date"]
        except:
            pass

        try:
            document["uid"] = document["uid"]["$uuid"]
        except:
            pass

        # Meal Plan
        try:
            document["startDate"] = document["startDate"]["$date"]
            document["endDate"] = document["endDate"]["$date"]

            meals = []
            for meal in document["meals"]:
                meal["date"] = meal["date"]["$date"]
                meals.append(meal)
            document["meals"] = meals
        except:
            pass

        return document

    def get_all(self, limit: int = None, order_by: str = None):
        if USE_MONGO:
            if order_by:
                documents = self.document.objects.order_by(str(order_by)).limit(limit)
            elif limit == None:
                documents = self.document.objects()
            else:
                documents = self.document.objects().limit(limit)

            docs = [BaseDocument._unpack_mongo(item) for item in documents]

            if limit == 1:
                return docs[0]
            return docs

        elif USE_SQL:
            session = create_session()
            list = [x.dict() for x in session.query(self.sql_model).all()]
            session.close()

            if limit == 1:
                return list[0]

            session.close()
            return list

    def get(
        self, match_value: str, match_key: str = None, limit=1
    ) -> dict or list[dict]:
        """Retrieves an entry from the database by matching a key/value pair. If no
        key is provided the class objects primary key will be used to match against.


        Args: \n
            match_value (str): A value used to match against the key/value in the database \n
            match_key (str, optional): They key to match the value against. Defaults to None. \n
            limit (int, optional): A limit to returned responses. Defaults to 1. \n

        Returns:
            dict or list[dict]:
        """
        if match_key == None:
            match_key = self.primary_key

        if USE_MONGO:
            document = self.document.objects.get(**{str(match_key): match_value})
            db_entry = BaseDocument._unpack_mongo(document)

        elif USE_SQL:
            session = create_session()
            result = (
                session.query(self.sql_model)
                .filter_by(**{match_key: match_value})
                .one()
            )

            db_entry = result.dict()

        else:
            raise Exception("No database type established")

        if limit == 1 and type(db_entry) == list:
            return db_entry[0]
        else:
            return db_entry

    def save_new(self, document: dict) -> dict:
        if USE_MONGO:
            new_document = self.document(**document)
            new_document.save()
            return BaseDocument._unpack_mongo(new_document)
        elif USE_SQL:
            return self.save_new_sql(document)

    def delete(self, primary_key_value) -> dict:
        if USE_MONGO:
            document = self.document.objects.get(**{str(self.primary_key): primary_key_value})

            if document:
                document.delete()
        elif USE_SQL:
            session = create_session()

            result = (
                session.query(self.sql_model)
                .filter_by(**{self.primary_key: primary_key_value})
                .one()
            )

            print(result.dict())
            session.delete(result)

            session.commit()
