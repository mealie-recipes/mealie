from __future__ import annotations

import random
from collections.abc import Iterable
from math import ceil
from typing import Any, Generic, TypeVar

from fastapi import HTTPException
from pydantic import UUID4, BaseModel
from sqlalchemy import Select, case, delete, func, select
from sqlalchemy.orm.session import Session
from sqlalchemy.sql import sqltypes

from mealie.core.root_logger import get_logger
from mealie.db.models._model_base import SqlAlchemyBase
from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import OrderDirection, PaginationBase, PaginationQuery
from mealie.schema.response.query_filter import QueryFilter

Schema = TypeVar("Schema", bound=MealieModel)
Model = TypeVar("Model", bound=SqlAlchemyBase)

T = TypeVar("T", bound="RepositoryGeneric")


class RepositoryGeneric(Generic[Schema, Model]):
    """A Generic BaseAccess Model method to perform common operations on the database

    Args:
        Generic ([Schema]): Represents the Pydantic Model
        Generic ([Model]): Represents the SqlAlchemyModel Model
    """

    user_id: UUID4 | None = None
    group_id: UUID4 | None = None
    session: Session

    def __init__(self, session: Session, primary_key: str, sql_model: type[Model], schema: type[Schema]) -> None:
        self.session = session
        self.primary_key = primary_key
        self.model = sql_model
        self.schema = schema

        self.logger = get_logger()

    def by_user(self: T, user_id: UUID4) -> T:
        self.user_id = user_id
        return self

    def by_group(self: T, group_id: UUID4) -> T:
        self.group_id = group_id
        return self

    def _log_exception(self, e: Exception) -> None:
        self.logger.error(f"Error processing query for Repo model={self.model.__name__} schema={self.schema.__name__}")
        self.logger.error(e)

    def _query(self, override_schema: type[MealieModel] | None = None, with_options=True):
        q = select(self.model)
        if with_options:
            schema = override_schema or self.schema
            return q.options(*schema.loader_options())
        else:
            return q

    def _filter_builder(self, **kwargs) -> dict[str, Any]:
        dct = {}

        if self.user_id:
            dct["user_id"] = self.user_id

        if self.group_id:
            dct["group_id"] = self.group_id

        return {**dct, **kwargs}

    def get_all(
        self,
        limit: int | None = None,
        order_by: str | None = None,
        order_descending: bool = True,
        start=0,
        override=None,
    ) -> list[Schema]:
        self.logger.warning('"get_all" method is deprecated; use "page_all" instead')

        # sourcery skip: remove-unnecessary-cast
        eff_schema = override or self.schema

        fltr = self._filter_builder()

        q = self._query(override_schema=eff_schema).filter_by(**fltr)

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
        result = self.session.execute(q.offset(start).limit(limit)).unique().scalars().all()
        return [eff_schema.from_orm(x) for x in result]

    def multi_query(
        self,
        query_by: dict[str, str | bool | int | UUID4],
        start=0,
        limit: int | None = None,
        override_schema=None,
        order_by: str | None = None,
    ) -> list[Schema]:
        # sourcery skip: remove-unnecessary-cast
        eff_schema = override_schema or self.schema

        fltr = self._filter_builder(**query_by)
        q = self._query(override_schema=eff_schema).filter_by(**fltr)

        if order_by:
            if order_attr := getattr(self.model, str(order_by)):
                order_attr = order_attr.desc()
                q = q.order_by(order_attr)

        q = q.offset(start).limit(limit)
        result = self.session.execute(q).unique().scalars().all()
        return [eff_schema.from_orm(x) for x in result]

    def _query_one(self, match_value: str | int | UUID4, match_key: str | None = None) -> Model:
        """
        Query the sql database for one item an return the sql alchemy model
        object. If no match key is provided the primary_key attribute will be used.
        """
        if match_key is None:
            match_key = self.primary_key

        fltr = self._filter_builder(**{match_key: match_value})
        return self.session.execute(self._query().filter_by(**fltr)).unique().scalars().one()

    def get_one(
        self, value: str | int | UUID4, key: str | None = None, any_case=False, override_schema=None
    ) -> Schema | None:
        key = key or self.primary_key
        eff_schema = override_schema or self.schema

        q = self._query(override_schema=eff_schema)

        if any_case:
            search_attr = getattr(self.model, key)
            q = q.where(func.lower(search_attr) == str(value).lower()).filter_by(**self._filter_builder())
        else:
            q = q.filter_by(**self._filter_builder(**{key: value}))

        result = self.session.execute(q).unique().scalars().one_or_none()

        if not result:
            return None

        return eff_schema.from_orm(result)

    def create(self, data: Schema | BaseModel | dict) -> Schema:
        data = data if isinstance(data, dict) else data.dict()
        new_document = self.model(session=self.session, **data)
        self.session.add(new_document)
        self.session.commit()
        self.session.refresh(new_document)

        return self.schema.from_orm(new_document)

    def create_many(self, data: Iterable[Schema | dict]) -> list[Schema]:
        new_documents = []
        for document in data:
            document = document if isinstance(document, dict) else document.dict()
            new_document = self.model(session=self.session, **document)
            new_documents.append(new_document)

        self.session.add_all(new_documents)
        self.session.commit()

        for created_document in new_documents:
            self.session.refresh(created_document)

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
        entry.update(session=self.session, **new_data)

        self.session.commit()
        return self.schema.from_orm(entry)

    def update_many(self, data: Iterable[Schema | dict]) -> list[Schema]:
        document_data_by_id: dict[str, dict] = {}
        for document in data:
            document_data = document if isinstance(document, dict) else document.dict()
            document_data_by_id[document_data["id"]] = document_data

        documents_to_update_query = self._query().filter(self.model.id.in_(list(document_data_by_id.keys())))
        documents_to_update = self.session.execute(documents_to_update_query).unique().scalars().all()

        updated_documents = []
        for document_to_update in documents_to_update:
            data = document_data_by_id[document_to_update.id]  # type: ignore
            document_to_update.update(session=self.session, **data)  # type: ignore
            updated_documents.append(document_to_update)

        self.session.commit()
        return [self.schema.from_orm(x) for x in updated_documents]

    def patch(self, match_value: str | int | UUID4, new_data: dict | BaseModel) -> Schema:
        new_data = new_data if isinstance(new_data, dict) else new_data.dict()

        entry = self._query_one(match_value=match_value)

        entry_as_dict = self.schema.from_orm(entry).dict()
        entry_as_dict.update(new_data)

        return self.update(match_value, entry_as_dict)

    def delete(self, value, match_key: str | None = None) -> Schema:
        match_key = match_key or self.primary_key

        result = self._query_one(value, match_key)
        results_as_model = self.schema.from_orm(result)

        try:
            self.session.delete(result)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return results_as_model

    def delete_many(self, values: Iterable) -> Schema:
        query = self._query().filter(self.model.id.in_(values))  # type: ignore
        results = self.session.execute(query).unique().scalars().all()
        results_as_model = [self.schema.from_orm(result) for result in results]

        try:
            # we create a delete statement for each row
            # we don't delete the whole query in one statement because postgres doesn't cascade correctly
            for result in results:
                self.session.delete(result)

            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return results_as_model  # type: ignore

    def delete_all(self) -> None:
        delete(self.model)
        self.session.commit()

    def count_all(self, match_key=None, match_value=None) -> int:
        q = select(func.count(self.model.id))
        if None not in [match_key, match_value]:
            q = q.filter_by(**{match_key: match_value})
        return self.session.scalar(q)

    def _count_attribute(
        self,
        attribute_name: str,
        attr_match: str | None = None,
        count=True,
        override_schema=None,
    ) -> int | list[Schema]:  # sourcery skip: assign-if-exp
        eff_schema = override_schema or self.schema

        if count:
            q = select(func.count(self.model.id)).filter(attribute_name == attr_match)
            return self.session.scalar(q)
        else:
            q = self._query(override_schema=eff_schema).filter(attribute_name == attr_match)
            return [eff_schema.from_orm(x) for x in self.session.execute(q).scalars().all()]

    def page_all(self, pagination: PaginationQuery, override=None) -> PaginationBase[Schema]:
        """
        pagination is a method to interact with the filtered database table and return a paginated result
        using the PaginationBase that provides several data points that are needed to manage pagination
        on the client side. This method does utilize the _filter_build method to ensure that the results
        are filtered by the user and group id when applicable.

        NOTE: When you provide an override you'll need to manually type the result of this method
        as the override, as the type system is not able to infer the result of this method.
        """
        eff_schema = override or self.schema

        q = self._query(override_schema=eff_schema, with_options=False)

        fltr = self._filter_builder()
        q = q.filter_by(**fltr)
        q, count, total_pages = self.add_pagination_to_query(q, pagination)

        # Apply options late, so they do not get used for counting
        q = q.options(*eff_schema.loader_options())
        try:
            data = self.session.execute(q).unique().scalars().all()
        except Exception as e:
            self._log_exception(e)
            self.session.rollback()
            raise e
        return PaginationBase(
            page=pagination.page,
            per_page=pagination.per_page,
            total=count,
            total_pages=total_pages,
            items=[eff_schema.from_orm(s) for s in data],
        )

    def add_pagination_to_query(self, query: Select, pagination: PaginationQuery) -> tuple[Select, int, int]:
        """
        Adds pagination data to an existing query.

        :returns:
            - query - modified query with pagination data
            - count - total number of records (without pagination)
            - total_pages - the total number of pages in the query
        """

        if pagination.query_filter:
            try:
                query_filter = QueryFilter(pagination.query_filter)
                query = query_filter.filter_query(query, model=self.model)

            except ValueError as e:
                self.logger.error(e)
                raise HTTPException(status_code=400, detail=str(e)) from e

        count_query = select(func.count()).select_from(query)
        count = self.session.scalar(count_query)
        if not count:
            count = 0

        # interpret -1 as "get_all"
        if pagination.per_page == -1:
            pagination.per_page = count

        try:
            total_pages = ceil(count / pagination.per_page)
        except ZeroDivisionError:
            total_pages = 0

        # interpret -1 as "last page"
        if pagination.page == -1:
            pagination.page = total_pages

        # failsafe for user input error
        if pagination.page < 1:
            pagination.page = 1

        if pagination.order_by:
            if order_attr := getattr(self.model, pagination.order_by, None):
                # queries handle uppercase and lowercase differently, which is undesirable
                if isinstance(order_attr.type, sqltypes.String):
                    order_attr = func.lower(order_attr)

                if pagination.order_direction == OrderDirection.asc:
                    order_attr = order_attr.asc()
                elif pagination.order_direction == OrderDirection.desc:
                    order_attr = order_attr.desc()

                query = query.order_by(order_attr)

            elif pagination.order_by == "random":
                # randomize outside of database, since not all db's can set random seeds
                # this solution is db-independent & stable to paging
                temp_query = query.with_only_columns(self.model.id)
                allids = self.session.execute(temp_query).scalars().all()  # fast because id is indexed
                order = list(range(len(allids)))
                random.seed(pagination.pagination_seed)
                random.shuffle(order)
                random_dict = dict(zip(allids, order, strict=True))
                case_stmt = case(random_dict, value=self.model.id)
                query = query.order_by(case_stmt)

        return query.limit(pagination.per_page).offset((pagination.page - 1) * pagination.per_page), count, total_pages
