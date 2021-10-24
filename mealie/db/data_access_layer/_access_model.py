from __future__ import annotations

from typing import Callable, Generic, TypeVar, Union

from sqlalchemy import func
from sqlalchemy.orm import load_only
from sqlalchemy.orm.session import Session

from mealie.core.root_logger import get_logger

logger = get_logger()

T = TypeVar("T")
D = TypeVar("D")


class AccessModel(Generic[T, D]):
    """A Generic BaseAccess Model method to perform common operations on the database

    Args:
        Generic ([T]): Represents the Pydantic Model
        Generic ([D]): Represents the SqlAlchemyModel Model
    """

    def __init__(self, session: Session, primary_key: Union[str, int], sql_model: D, schema: T) -> None:
        self.session = session
        self.primary_key = primary_key
        self.sql_model = sql_model
        self.schema = schema
        self.observers: list = []

    def subscribe(self, func: Callable) -> None:
        self.observers.append(func)

    # TODO: Run Observer in Async Background Task
    def update_observers(self) -> None:
        if self.observers:
            for observer in self.observers:
                observer()

    def get_all(self, limit: int = None, order_by: str = None, start=0, override_schema=None) -> list[T]:
        eff_schema = override_schema or self.schema

        order_attr = None
        if order_by:
            order_attr = getattr(self.sql_model, str(order_by))
            order_attr = order_attr.desc()

            return [
                eff_schema.from_orm(x)
                for x in self.session.query(self.sql_model).order_by(order_attr).offset(start).limit(limit).all()
            ]

        return [eff_schema.from_orm(x) for x in self.session.query(self.sql_model).offset(start).limit(limit).all()]

    def multi_query(
        self,
        query_by: dict[str, str],
        start=0,
        limit: int = None,
        override_schema=None,
        order_by: str = None,
    ) -> list[T]:
        eff_schema = override_schema or self.schema

        order_attr = None
        if order_by:
            order_attr = getattr(self.sql_model, str(order_by))
            order_attr = order_attr.desc()

        return [
            eff_schema.from_orm(x)
            for x in self.session.query(self.sql_model)
            .filter_by(**query_by)
            .order_by(order_attr)
            .offset(start)
            .limit(limit)
            .all()
        ]

    def get_all_limit_columns(self, fields: list[str], limit: int = None) -> list[D]:
        """Queries the database for the selected model. Restricts return responses to the
        keys specified under "fields"

        Args:
            session (Session): Database Session Object
            fields (list[str]): list of column names to query
            limit (int): A limit of values to return

        Returns:
            list[SqlAlchemyBase]: Returns a list of ORM objects
        """
        return self.session.query(self.sql_model).options(load_only(*fields)).limit(limit).all()

    def get_all_primary_keys(self) -> list[str]:
        """Queries the database of the selected model and returns a list
        of all primary_key values

        Args:
            session (Session): Database Session object

        Returns:
            list[str]:
        """
        results = self.session.query(self.sql_model).options(load_only(str(self.primary_key)))
        results_as_dict = [x.dict() for x in results]
        return [x.get(self.primary_key) for x in results_as_dict]

    def _query_one(self, match_value: str, match_key: str = None) -> D:
        """
        Query the sql database for one item an return the sql alchemy model
        object. If no match key is provided the primary_key attribute will be used.
        """
        if match_key is None:
            match_key = self.primary_key

        return self.session.query(self.sql_model).filter_by(**{match_key: match_value}).one()

    def get_one(self, value: str | int, key: str = None, any_case=False, override_schema=None) -> T:
        key = key or self.primary_key

        if any_case:
            search_attr = getattr(self.sql_model, key)
            result = self.session.query(self.sql_model).filter(func.lower(search_attr) == key.lower()).one_or_none()
        else:
            result = self.session.query(self.sql_model).filter_by(**{key: value}).one_or_none()

        if not result:
            return

        eff_schema = override_schema or self.schema
        return eff_schema.from_orm(result)

    def get(
        self, match_value: str, match_key: str = None, limit=1, any_case=False, override_schema=None
    ) -> T | list[T]:
        """Retrieves an entry from the database by matching a key/value pair. If no
        key is provided the class objects primary key will be used to match against.


        Args:
            match_value (str): A value used to match against the key/value in the database
            match_key (str, optional): They key to match the value against. Defaults to None.
            limit (int, optional): A limit to returned responses. Defaults to 1.

        Returns:
            dict or list[dict]:

        """
        match_key = match_key or self.primary_key

        if any_case:
            search_attr = getattr(self.sql_model, match_key)
            result = (
                self.session.query(self.sql_model)
                .filter(func.lower(search_attr) == match_value.lower())
                .limit(limit)
                .all()
            )
        else:
            result = self.session.query(self.sql_model).filter_by(**{match_key: match_value}).limit(limit).all()

        eff_schema = override_schema or self.schema

        if limit == 1:
            try:
                return eff_schema.from_orm(result[0])
            except IndexError:
                return None

        return [eff_schema.from_orm(x) for x in result]

    def create(self, document: T) -> T:
        """Creates a new database entry for the given SQL Alchemy Model.

        Args:
            session (Session): A Database Session
            document (dict): A python dictionary representing the data structure

        Returns:
            dict: A dictionary representation of the database entry
        """
        document = document if isinstance(document, dict) else document.dict()
        new_document = self.sql_model(session=self.session, **document)
        self.session.add(new_document)
        self.session.commit()
        self.session.refresh(new_document)

        if self.observers:
            self.update_observers()

        return self.schema.from_orm(new_document)

    def update(self, match_value: str, new_data: dict) -> T:
        """Update a database entry.
        Args:
            session (Session): Database Session
            match_value (str): Match "key"
            new_data (str): Match "value"

        Returns:
            dict: Returns a dictionary representation of the database entry
        """
        new_data = new_data if isinstance(new_data, dict) else new_data.dict()

        entry = self._query_one(match_value=match_value)
        entry.update(session=self.session, **new_data)

        if self.observers:
            self.update_observers()

        self.session.commit()
        return self.schema.from_orm(entry)

    def patch(self, match_value: str, new_data: dict) -> T:
        new_data = new_data if isinstance(new_data, dict) else new_data.dict()

        entry = self._query_one(match_value=match_value)

        if not entry:
            return

        entry_as_dict = self.schema.from_orm(entry).dict()
        entry_as_dict.update(new_data)

        return self.update(match_value, entry_as_dict)

    def delete(self, primary_key_value) -> D:
        result = self.session.query(self.sql_model).filter_by(**{self.primary_key: primary_key_value}).one()
        results_as_model = self.schema.from_orm(result)

        self.session.delete(result)
        self.session.commit()

        if self.observers:
            self.update_observers()

        return results_as_model

    def delete_all(self) -> None:
        self.session.query(self.sql_model).delete()
        self.session.commit()

        if self.observers:
            self.update_observers()

    def count_all(self, match_key=None, match_value=None) -> int:
        if None in [match_key, match_value]:
            return self.session.query(self.sql_model).count()
        else:
            return self.session.query(self.sql_model).filter_by(**{match_key: match_value}).count()

    def _count_attribute(
        self, attribute_name: str, attr_match: str = None, count=True, override_schema=None
    ) -> Union[int, T]:
        eff_schema = override_schema or self.schema
        # attr_filter = getattr(self.sql_model, attribute_name)

        if count:
            return self.session.query(self.sql_model).filter(attribute_name == attr_match).count()  # noqa: 711
        else:
            return [
                eff_schema.from_orm(x)
                for x in self.session.query(self.sql_model).filter(attribute_name == attr_match).all()  # noqa: 711
            ]
