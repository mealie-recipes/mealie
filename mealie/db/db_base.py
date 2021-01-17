from typing import Union

from sqlalchemy.orm.session import Session

from db.sql.db_session import create_session
from db.sql.model_base import SqlAlchemyBase


class BaseDocument:
    def __init__(self) -> None:
        self.primary_key: str
        self.store: str
        self.sql_model: SqlAlchemyBase
        self.create_session = create_session

    def get_all(self, limit: int = None, order_by: str = None):
        session = create_session()
        list = [x.dict() for x in session.query(self.sql_model).all()]
        session.close()

        if limit == 1:
            return list[0]

        return list

    def _query_one(
        self, match_value: str, match_key: str = None
    ) -> Union[Session, SqlAlchemyBase]:
        """Query the sql database for one item an return the sql alchemy model
        object. If no match key is provided the primary_key attribute will be used.

        Args:
            match_value (str): The value to use in the query
            match_key (str, optional): the key/property to match against. Defaults to None.

        Returns:
            Union[Session, SqlAlchemyBase]: Will return both the session and found model
        """
        session = self.create_session()

        if match_key == None:
            match_key = self.primary_key

        result = (
            session.query(self.sql_model).filter_by(**{match_key: match_value}).one()
        )

        return session, result

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

        session = self.create_session()
        result = (
            session.query(self.sql_model).filter_by(**{match_key: match_value}).one()
        )
        db_entry = result.dict()
        session.close()

        return db_entry

    def save_new(self, document: dict) -> dict:
        session = self.create_session()
        new_document = self.sql_model(**document)
        session.add(new_document)
        return_data = new_document.dict()
        session.commit()


        session.close()
        return return_data

    def update(self, match_value, new_data) -> dict:
        session, entry = self._query_one(match_value=match_value)
        entry.update(session=session, **new_data)
        return_data = entry.dict()
        session.commit()

        session.close()

        return return_data

    def delete(self, primary_key_value) -> dict:
        session = create_session()

        result = (
            session.query(self.sql_model)
            .filter_by(**{self.primary_key: primary_key_value})
            .one()
        )

        session.delete(result)

        session.commit()
        session.close()
