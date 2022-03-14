from collections.abc import Callable
from typing import Any, Generic, TypeVar, Union

from pydantic import UUID4, BaseModel
from sqlalchemy import func
from sqlalchemy.orm import load_only
from sqlalchemy.orm.session import Session

T = TypeVar("T", bound=BaseModel)
D = TypeVar("D")


class RepositoryGeneric(Generic[T, D]):
    """A Generic BaseAccess Model method to perform common operations on the database

    Args:
        Generic ([T]): Represents the Pydantic Model
        Generic ([D]): Represents the SqlAlchemyModel Model
    """

    def __init__(self, session: Session, primary_key: str, sql_model: type[D], schema: type[T]) -> None:
        self.session = session
        self.primary_key = primary_key
        self.sql_model = sql_model
        self.schema = schema
        self.observers: list = []

        self.limit_by_group = False
        self.user_id: UUID4 = None

        self.limit_by_user = False
        self.group_id: UUID4 = None

    def subscribe(self, func: Callable) -> None:
        self.observers.append(func)

    def by_user(self, user_id: UUID4) -> "RepositoryGeneric[T, D]":
        self.limit_by_user = True
        self.user_id = user_id
        return self

    def by_group(self, group_id: UUID4) -> "RepositoryGeneric[T, D]":
        self.limit_by_group = True
        self.group_id = group_id
        return self

    def _filter_builder(self, **kwargs) -> dict[str, Any]:
        dct = {}

        if self.limit_by_user:
            dct["user_id"] = self.user_id

        if self.limit_by_group:
            dct["group_id"] = self.group_id

        return {**dct, **kwargs}

    # TODO: Run Observer in Async Background Task
    def update_observers(self) -> None:
        if self.observers:
            for observer in self.observers:
                observer()

    def get_all(self, limit: int = None, order_by: str = None, start=0, override_schema=None) -> list[T]:
        eff_schema = override_schema or self.schema

        filter = self._filter_builder()

        order_attr = None
        if order_by:
            order_attr = getattr(self.sql_model, str(order_by))
            order_attr = order_attr.desc()

            return [
                eff_schema.from_orm(x)
                for x in self.session.query(self.sql_model)
                .order_by(order_attr)
                .filter_by(**filter)
                .offset(start)
                .limit(limit)
                .all()
            ]

        return [
            eff_schema.from_orm(x)
            for x in self.session.query(self.sql_model).filter_by(**filter).offset(start).limit(limit).all()
        ]

    def multi_query(
        self,
        query_by: dict[str, str | bool | int | UUID4],
        start=0,
        limit: int = None,
        override_schema=None,
        order_by: str = None,
    ) -> list[T]:
        eff_schema = override_schema or self.schema

        filer = self._filter_builder(**query_by)

        order_attr = None
        if order_by:
            order_attr = getattr(self.sql_model, str(order_by))
            order_attr = order_attr.desc()

        return [
            eff_schema.from_orm(x)
            for x in self.session.query(self.sql_model)
            .filter_by(**filer)
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

    def _query_one(self, match_value: str | int | UUID4, match_key: str = None) -> D:
        """
        Query the sql database for one item an return the sql alchemy model
        object. If no match key is provided the primary_key attribute will be used.
        """
        if match_key is None:
            match_key = self.primary_key

        filter = self._filter_builder(**{match_key: match_value})
        return self.session.query(self.sql_model).filter_by(**filter).one()

    def get_one(self, value: str | int | UUID4, key: str = None, any_case=False, override_schema=None) -> T | None:
        key = key or self.primary_key

        q = self.session.query(self.sql_model)

        if any_case:
            search_attr = getattr(self.sql_model, key)
            q = q.filter(func.lower(search_attr) == key.lower()).filter_by(**self._filter_builder())
        else:
            q = self.session.query(self.sql_model).filter_by(**self._filter_builder(**{key: value}))

        result = q.one_or_none()

        if not result:
            return None

        eff_schema = override_schema or self.schema
        return eff_schema.from_orm(result)

    def get(
        self, match_value: str | int | UUID4, match_key: str = None, limit=1, any_case=False, override_schema=None
    ) -> T | list[T] | None:
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
                .filter(func.lower(search_attr) == match_value.lower())  # type: ignore
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

    def create(self, document: T | BaseModel) -> T:
        """Creates a new database entry for the given SQL Alchemy Model.

        Args:
            session (Session): A Database Session
            document (dict): A python dictionary representing the data structure

        Returns:
            dict: A dictionary representation of the database entry
        """
        document = document if isinstance(document, dict) else document.dict()
        new_document = self.sql_model(session=self.session, **document)  # type: ignore
        self.session.add(new_document)
        self.session.commit()
        self.session.refresh(new_document)

        if self.observers:
            self.update_observers()

        return self.schema.from_orm(new_document)

    def update(self, match_value: str | int | UUID4, new_data: dict | BaseModel) -> T:
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
        entry.update(session=self.session, **new_data)  # type: ignore

        if self.observers:
            self.update_observers()

        self.session.commit()
        return self.schema.from_orm(entry)

    def patch(self, match_value: str | int | UUID4, new_data: dict | BaseModel) -> T | None:
        new_data = new_data if isinstance(new_data, dict) else new_data.dict()

        entry = self._query_one(match_value=match_value)

        if not entry:
            # TODO: Should raise exception
            return None

        entry_as_dict = self.schema.from_orm(entry).dict()
        entry_as_dict.update(new_data)

        return self.update(match_value, entry_as_dict)

    def delete(self, primary_key_value) -> D:
        result = self.session.query(self.sql_model).filter_by(**{self.primary_key: primary_key_value}).one()
        results_as_model = self.schema.from_orm(result)

        try:
            self.session.delete(result)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

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
        self,
        attribute_name: str,
        attr_match: str = None,
        count=True,
        override_schema=None,
    ) -> Union[int, list[T]]:
        eff_schema = override_schema or self.schema
        # attr_filter = getattr(self.sql_model, attribute_name)

        if count:
            return self.session.query(self.sql_model).filter(attribute_name == attr_match).count()  # noqa: 711
        else:
            return [
                eff_schema.from_orm(x)
                for x in self.session.query(self.sql_model).filter(attribute_name == attr_match).all()  # noqa: 711
            ]

    def create_many(self, documents: list[T]) -> list[T]:
        new_documents = []
        for document in documents:
            document = document if isinstance(document, dict) else document.dict()
            new_document = self.sql_model(session=self.session, **document)  # type: ignore
            new_documents.append(new_document)

        self.session.add_all(new_documents)
        self.session.commit()
        self.session.refresh(new_documents)

        return [self.schema.from_orm(x) for x in new_documents]
