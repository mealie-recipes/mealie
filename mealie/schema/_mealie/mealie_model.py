from __future__ import annotations

from collections.abc import Sequence
from enum import Enum
from typing import ClassVar, Protocol, TypeVar

from humps.main import camelize
from pydantic import UUID4, BaseModel, ConfigDict
from sqlalchemy import Select, desc, func, or_, text
from sqlalchemy.orm import InstrumentedAttribute, Session
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models._model_base import SqlAlchemyBase

T = TypeVar("T", bound=BaseModel)


class SearchType(Enum):
    fuzzy = "fuzzy"
    tokenized = "tokenized"


class MealieModel(BaseModel):
    _fuzzy_similarity_threshold: ClassVar[float] = 0.5
    _normalize_search: ClassVar[bool] = False
    _searchable_properties: ClassVar[list[str]] = []
    """
    Searchable properties for the search API.
    The first property will be used for sorting (order_by)
    """
    model_config = ConfigDict(alias_generator=camelize, populate_by_name=True)

    def cast(self, cls: type[T], **kwargs) -> T:
        """
        Cast the current model to another with additional arguments. Useful for
        transforming DTOs into models that are saved to a database
        """
        create_data = {field: getattr(self, field) for field in self.__fields__ if field in cls.__fields__}
        create_data.update(kwargs or {})
        return cls(**create_data)

    def map_to(self, dest: T) -> T:
        """
        Map matching values from the current model to another model. Model returned
        for method chaining.
        """

        for field in self.model_fields:
            if field in dest.model_fields:
                setattr(dest, field, getattr(self, field))

        return dest

    def map_from(self, src: BaseModel):
        """
        Map matching values from another model to the current model.
        """

        for field in src.model_fields:
            if field in self.model_fields:
                setattr(self, field, getattr(src, field))

    def merge(self, src: T, replace_null=False):
        """
        Replace matching values from another instance to the current instance.
        """

        for field in src.model_fields:
            val = getattr(src, field)
            if field in self.model_fields and (val is not None or replace_null):
                setattr(self, field, val)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return []

    @classmethod
    def filter_search_query(
        cls,
        db_model: type[SqlAlchemyBase],
        query: Select,
        session: Session,
        search_type: SearchType,
        search: str,
        search_list: list[str],
    ) -> Select:
        """
        Filters a search query based on model attributes

        Can be overridden to support a more advanced search
        """

        if not cls._searchable_properties:
            raise AttributeError("Not Implemented")

        model_properties: list[InstrumentedAttribute] = [getattr(db_model, prop) for prop in cls._searchable_properties]
        if search_type is SearchType.fuzzy:
            session.execute(text(f"set pg_trgm.word_similarity_threshold = {cls._fuzzy_similarity_threshold};"))
            filters = [prop.op("%>")(search) for prop in model_properties]

            # trigram ordering by the first searchable property
            return query.filter(or_(*filters)).order_by(func.least(model_properties[0].op("<->>")(search)))
        else:
            filters = []
            for prop in model_properties:
                filters.extend([prop.like(f"%{s}%") for s in search_list])

            # order by how close the result is to the first searchable property
            return query.filter(or_(*filters)).order_by(desc(model_properties[0].like(f"%{search}%")))


class HasUUID(Protocol):
    id: UUID4


def extract_uuids(models: Sequence[HasUUID]) -> list[UUID4]:
    return [x.id for x in models]
