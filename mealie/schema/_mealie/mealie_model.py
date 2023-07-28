from __future__ import annotations

from collections.abc import Sequence
from enum import Enum
from typing import Protocol, TypeVar

from humps.main import camelize
from pydantic import UUID4, BaseModel
from sqlalchemy import Select
from sqlalchemy.orm import Session
from sqlalchemy.orm.interfaces import LoaderOption

T = TypeVar("T", bound=BaseModel)


class SearchType(Enum):
    fuzzy = "fuzzy"
    tokenized = "tokenized"


class MealieModel(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True

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

        for field in self.__fields__:
            if field in dest.__fields__:
                setattr(dest, field, getattr(self, field))

        return dest

    def map_from(self, src: BaseModel):
        """
        Map matching values from another model to the current model.
        """

        for field in src.__fields__:
            if field in self.__fields__:
                setattr(self, field, getattr(src, field))

    def merge(self, src: T, replace_null=False):
        """
        Replace matching values from another instance to the current instance.
        """

        for field in src.__fields__:
            val = getattr(src, field)
            if field in self.__fields__ and (val is not None or replace_null):
                setattr(self, field, val)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return []

    @classmethod
    def filter_search_query(
        cls, query: Select, session: Session, search_type: SearchType, search: str, search_list: list[str]
    ) -> Select:
        """
        Filters a search query based on model attributes

        Should be overridden by any classes supporting search
        """

        raise AttributeError("Not Implemented")


class HasUUID(Protocol):
    id: UUID4


def extract_uuids(models: Sequence[HasUUID]) -> list[UUID4]:
    return [x.id for x in models]
