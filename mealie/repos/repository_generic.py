from typing import Any, Generic, TypeVar, Union

from pydantic import UUID4, BaseModel
from sqlalchemy import func
from sqlalchemy.orm.session import Session

from mealie.core.root_logger import get_logger
from mealie.schema.response.pagination import OrderDirection, PaginationBase, PaginationQuery

Schema = TypeVar("Schema", bound=BaseModel)
Model = TypeVar("Model")


class RepositoryGeneric(Generic[Schema, Model]):
    """A Generic BaseAccess Model method to perform common operations on the database

    Args:
        Generic ([Schema]): Represents the Pydantic Model
        Generic ([Model]): Represents the SqlAlchemyModel Model
    """

    user_id: UUID4 = None
    group_id: UUID4 = None

    def __init__(self, session: Session, primary_key: str, sql_model: type[Model], schema: type[Schema]) -> None:
        self.session = session
        self.primary_key = primary_key
        self.model = sql_model
        self.schema = schema

        self.logger = get_logger()

    def by_user(self, user_id: UUID4) -> "RepositoryGeneric[Schema, Model]":
        self.user_id = user_id
        return self

    def by_group(self, group_id: UUID4) -> "RepositoryGeneric[Schema, Model]":
        self.group_id = group_id
        return self

    def _log_exception(self, e: Exception) -> None:
        self.logger.error(f"Error processing query for Repo model={self.model.__name__} schema={self.schema.__name__}")
        self.logger.error(e)

    def _query(self):
        return self.session.query(self.model)

    def _filter_builder(self, **kwargs) -> dict[str, Any]:
        dct = {}

        if self.user_id:
            dct["user_id"] = self.user_id

        if self.group_id:
            dct["group_id"] = self.group_id

        return {**dct, **kwargs}

    def get_all(
        self, limit: int = None, order_by: str = None, order_descending: bool = True, start=0, override=None
    ) -> list[Schema]:
        # sourcery skip: remove-unnecessary-cast
        eff_schema = override or self.schema

        fltr = self._filter_builder()

        q = self._query().filter_by(**fltr)

        if order_by:
            try:
                order_attr = getattr(self.model, str(order_by))
                if order_descending:
                    order_attr = order_attr.desc()

                else:
                    order_attr = order_attr.asc()

                q = q.order_by(order_attr)

            except AttributeError:
                self.logger.info(f'Attempted to sort by unknown sort property "{order_by}"; ignoring')

        return [eff_schema.from_orm(x) for x in q.offset(start).limit(limit).all()]

    def multi_query(
        self,
        query_by: dict[str, str | bool | int | UUID4],
        start=0,
        limit: int = None,
        override_schema=None,
        order_by: str = None,
    ) -> list[Schema]:
        # sourcery skip: remove-unnecessary-cast
        eff_schema = override_schema or self.schema

        fltr = self._filter_builder(**query_by)
        q = self._query().filter_by(**fltr)

        if order_by:
            if order_attr := getattr(self.model, str(order_by)):
                order_attr = order_attr.desc()
                q = q.order_by(order_attr)

        return [eff_schema.from_orm(x) for x in q.offset(start).limit(limit).all()]

    def _query_one(self, match_value: str | int | UUID4, match_key: str = None) -> Model:
        """
        Query the sql database for one item an return the sql alchemy model
        object. If no match key is provided the primary_key attribute will be used.
        """
        if match_key is None:
            match_key = self.primary_key

        fltr = self._filter_builder(**{match_key: match_value})
        return self._query().filter_by(**fltr).one()

    def get_one(self, value: str | int | UUID4, key: str = None, any_case=False, override_schema=None) -> Schema | None:
        key = key or self.primary_key

        q = self.session.query(self.model)

        if any_case:
            search_attr = getattr(self.model, key)
            q = q.where(func.lower(search_attr) == str(value).lower()).filter_by(**self._filter_builder())
        else:
            q = q.filter_by(**self._filter_builder(**{key: value}))

        result = q.one_or_none()

        if not result:
            return None

        eff_schema = override_schema or self.schema
        return eff_schema.from_orm(result)

    def create(self, data: Schema | BaseModel | dict) -> Schema:
        data = data if isinstance(data, dict) else data.dict()
        new_document = self.model(session=self.session, **data)  # type: ignore
        self.session.add(new_document)
        self.session.commit()
        self.session.refresh(new_document)

        return self.schema.from_orm(new_document)

    def create_many(self, data: list[Schema | dict]) -> list[Schema]:
        new_documents = []
        for document in data:
            document = document if isinstance(document, dict) else document.dict()
            new_document = self.model(session=self.session, **document)  # type: ignore
            new_documents.append(new_document)

        self.session.add_all(new_documents)
        self.session.commit()
        self.session.refresh(new_documents)

        return [self.schema.from_orm(x) for x in new_documents]

    def update(self, match_value: str | int | UUID4, new_data: dict | BaseModel) -> Schema:
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

        self.session.commit()
        return self.schema.from_orm(entry)

    def patch(self, match_value: str | int | UUID4, new_data: dict | BaseModel) -> Schema:
        new_data = new_data if isinstance(new_data, dict) else new_data.dict()

        entry = self._query_one(match_value=match_value)

        entry_as_dict = self.schema.from_orm(entry).dict()
        entry_as_dict.update(new_data)

        return self.update(match_value, entry_as_dict)

    def delete(self, value, match_key: str | None = None) -> Schema:
        match_key = match_key or self.primary_key

        result = self._query().filter_by(**{match_key: value}).one()
        results_as_model = self.schema.from_orm(result)

        try:
            self.session.delete(result)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return results_as_model

    def delete_all(self) -> None:
        self._query().delete()
        self.session.commit()

    def count_all(self, match_key=None, match_value=None) -> int:
        if None in [match_key, match_value]:
            return self._query().count()
        else:
            return self._query().filter_by(**{match_key: match_value}).count()

    def _count_attribute(
        self,
        attribute_name: str,
        attr_match: str = None,
        count=True,
        override_schema=None,
    ) -> Union[int, list[Schema]]:  # sourcery skip: assign-if-exp
        eff_schema = override_schema or self.schema

        q = self._query().filter(attribute_name == attr_match)

        if count:
            return q.count()
        else:
            return [eff_schema.from_orm(x) for x in q.all()]

    def pagination(self, pagination: PaginationQuery, override=None) -> PaginationBase[Schema]:
        """
        pagination is a method to interact with the filtered database table and return a paginated result
        using the PaginationBase that provides several data points that are needed to manage pagination
        on the client side. This method does utilize the _filter_build method to ensure that the results
        are filtered by the user and group id when applicable.

        NOTE: When you provide an override you'll need to manually type the result of this method
        as the override, as the type system, is not able to infer the result of this method.
        """
        eff_schema = override or self.schema

        q = self.session.query(self.model)

        fltr = self._filter_builder()
        q = q.filter_by(**fltr)

        count = q.count()

        if pagination.order_by:
            if order_attr := getattr(self.model, pagination.order_by, None):
                if pagination.order_direction == OrderDirection.asc:
                    order_attr = order_attr.asc()
                elif pagination.order_direction == OrderDirection.desc:
                    order_attr = order_attr.desc()

                q = q.order_by(order_attr)

        q = q.limit(pagination.per_page).offset((pagination.page - 1) * pagination.per_page)

        try:
            data = q.all()
        except Exception as e:
            self._log_exception(e)
            self.session.rollback()
            raise e

        return PaginationBase(
            page=pagination.page,
            per_page=pagination.per_page,
            total=count,
            total_pages=int(count / pagination.per_page) + 1,
            data=[eff_schema.from_orm(s) for s in data],
        )
