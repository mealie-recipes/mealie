from typing import List

from mealie.db.models.model_base import SqlAlchemyBase
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import load_only
from sqlalchemy.orm.session import Session


class BaseDocument:
    def __init__(self) -> None:
        self.primary_key: str
        self.store: str
        self.sql_model: SqlAlchemyBase
        self.orm_mode = False
        self.schema: BaseModel

    # TODO: Improve Get All Query Functionality
    def get_all(self, session: Session, limit: int = None, order_by: str = None, override_schema=None) -> List[dict]:
        eff_schema = override_schema or self.schema

        return [eff_schema.from_orm(x) for x in session.query(self.sql_model).limit(limit).all()]

    def get_all_limit_columns(self, session: Session, fields: List[str], limit: int = None) -> List[SqlAlchemyBase]:
        """Queries the database for the selected model. Restricts return responses to the
        keys specified under "fields"

        Args: \n
            session (Session): Database Session Object
            fields (List[str]): List of column names to query
            limit (int): A limit of values to return

        Returns:
            list[SqlAlchemyBase]: Returns a list of ORM objects
        """
        return session.query(self.sql_model).options(load_only(*fields)).limit(limit).all()

    def get_all_primary_keys(self, session: Session) -> List[str]:
        """Queries the database of the selected model and returns a list
        of all primary_key values

        Args: \n
            session (Session): Database Session object

        Returns:
            list[str]:
        """
        results = session.query(self.sql_model).options(load_only(str(self.primary_key)))
        results_as_dict = [x.dict() for x in results]
        return [x.get(self.primary_key) for x in results_as_dict]

    def _query_one(self, session: Session, match_value: str, match_key: str = None) -> SqlAlchemyBase:
        """Query the sql database for one item an return the sql alchemy model
        object. If no match key is provided the primary_key attribute will be used.

        Args: \n
            match_value (str): The value to use in the query
            match_key (str, optional): the key/property to match against. Defaults to None.

        Returns:
            Union[Session, SqlAlchemyBase]: Will return both the session and found model
        """
        if match_key is None:
            match_key = self.primary_key

        return session.query(self.sql_model).filter_by(**{match_key: match_value}).one()

    def get(
        self, session: Session, match_value: str, match_key: str = None, limit=1, any_case=False
    ) -> BaseModel or List[BaseModel]:
        """Retrieves an entry from the database by matching a key/value pair. If no
        key is provided the class objects primary key will be used to match against.


        Args: \n
            match_value (str): A value used to match against the key/value in the database \n
            match_key (str, optional): They key to match the value against. Defaults to None. \n
            limit (int, optional): A limit to returned responses. Defaults to 1. \n

        Returns:
            dict or list[dict]:
        """
        if match_key is None:
            match_key = self.primary_key

        if any_case:
            search_attr = getattr(self.sql_model, match_key)
            result = (
                session.query(self.sql_model).filter(func.lower(search_attr) == match_value.lower()).limit(limit).all()
            )
        else:
            result = session.query(self.sql_model).filter_by(**{match_key: match_value}).limit(limit).all()

        if limit == 1:
            try:
                return self.schema.from_orm(result[0])
            except IndexError:
                return None
        return [self.schema.from_orm(x) for x in result]

    def create(self, session: Session, document: dict) -> BaseModel:
        """Creates a new database entry for the given SQL Alchemy Model.

        Args: \n
            session (Session): A Database Session
            document (dict): A python dictionary representing the data structure

        Returns:
            dict: A dictionary representation of the database entry
        """
        new_document = self.sql_model(session=session, **document)
        session.add(new_document)
        session.commit()

        return self.schema.from_orm(new_document)

    def update(self, session: Session, match_value: str, new_data: str) -> BaseModel:
        """Update a database entry.
        Args: \n
            session (Session): Database Session
            match_value (str): Match "key"
            new_data (str): Match "value"

        Returns:
            dict: Returns a dictionary representation of the database entry
        """

        entry = self._query_one(session=session, match_value=match_value)
        entry.update(session=session, **new_data)

        session.commit()
        return self.schema.from_orm(entry)

    def delete(self, session: Session, primary_key_value) -> dict:
        result = session.query(self.sql_model).filter_by(**{self.primary_key: primary_key_value}).one()

        session.delete(result)
        session.commit()
