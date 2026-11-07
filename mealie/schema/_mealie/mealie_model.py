from __future__ import annotations

import re
import types
from collections.abc import Sequence
from datetime import UTC, datetime
from enum import Enum
from functools import cache
from typing import Annotated, Any, ClassVar, Protocol, Self, Union, get_args, get_origin

from humps.main import camelize
from pydantic import UUID4, AliasChoices, BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import Select, desc, func, or_, text
from sqlalchemy.orm import InstrumentedAttribute, Session
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models._model_base import SqlAlchemyBase

HOUR_ONLY_TZ_PATTERN = re.compile(r"[+-]\d{2}$")


def _may_hold_datetime(annotation: Any) -> bool:
    if annotation is Any or annotation is object:
        return True
    if isinstance(annotation, type):
        return issubclass(annotation, datetime)
    if get_origin(annotation) is Annotated:
        return _may_hold_datetime(get_args(annotation)[0])
    if get_origin(annotation) in (Union, types.UnionType):
        return any(_may_hold_datetime(arg) for arg in get_args(annotation))
    # Unresolved forward refs, TypeVars and the like: check them at runtime to be safe
    return get_origin(annotation) is None


@cache
def _exact_datetime_fields(cls: type[BaseModel]) -> tuple[str, ...]:
    return tuple(name for name, info in cls.model_fields.items() if info.annotation == datetime)


@cache
def _datetime_fields(cls: type[BaseModel]) -> tuple[str, ...]:
    """
    Fields that can hold a datetime. The timezone validators run on every model, nested ones
    included, so checking every field of every model was a noticeable part of list responses.
    """
    return tuple(name for name, info in cls.model_fields.items() if _may_hold_datetime(info.annotation))


def UpdatedAtField(*args, **kwargs):
    """
    Wrapper for Pydantic's Field, which sets default values for our update_at aliases

    Since the database stores this value as update_at, we want to accept this as a possible value
    """

    kwargs.pop("alias", None)
    kwargs.pop("alias_generator", None)

    # ensure the alias is not overwritten by the generator, if there is one
    # https://docs.pydantic.dev/latest/concepts/alias/#alias-priority
    kwargs["alias_priority"] = 2

    kwargs["validation_alias"] = AliasChoices("update_at", "updateAt", "updated_at", "updatedAt")
    kwargs["serialization_alias"] = "updatedAt"

    return Field(*args, **kwargs)


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

    @model_validator(mode="before")
    @classmethod
    def fix_hour_only_tz[T: BaseModel](cls, data: T) -> T:
        """
        Fixes datetimes with timezones that only have the hour portion.

        Pydantic assumes timezones are in the format +HH:MM, but postgres returns +HH.
        https://github.com/pydantic/pydantic/issues/8609
        """
        for field in _exact_datetime_fields(cls):
            try:
                if not isinstance(val := getattr(data, field), str):
                    continue
            except AttributeError:
                continue
            if re.search(HOUR_ONLY_TZ_PATTERN, val):
                setattr(data, field, val + ":00")

        return data

    @model_validator(mode="after")
    def set_tz_info(self) -> Self:
        """
        Adds UTC timezone information to all datetimes in the model.
        The server stores everything in UTC without timezone info.
        """
        for field in _datetime_fields(self.__class__):
            val = getattr(self, field)
            if not isinstance(val, datetime):
                continue
            if not val.tzinfo:
                setattr(self, field, val.replace(tzinfo=UTC))

        return self

    def cast[T: BaseModel](self, cls: type[T], **kwargs) -> T:
        """
        Cast the current model to another with additional arguments. Useful for
        transforming DTOs into models that are saved to a database
        """
        create_data = {
            field: getattr(self, field) for field in self.__class__.model_fields if field in cls.model_fields
        }
        create_data.update(kwargs or {})
        return cls(**create_data)

    def map_to[T: BaseModel](self, dest: T) -> T:
        """
        Map matching values from the current model to another model. Model returned
        for method chaining.
        """

        for field in self.__class__.model_fields:
            if field in dest.__class__.model_fields:
                setattr(dest, field, getattr(self, field))

        return dest

    def map_from(self, src: BaseModel):
        """
        Map matching values from another model to the current model.
        """

        for field in src.__class__.model_fields:
            if field in self.__class__.model_fields:
                setattr(self, field, getattr(src, field))

    def merge[T: BaseModel](self, src: T, replace_null=False):
        """
        Replace matching values from another instance to the current instance.
        """

        for field in src.__class__.model_fields:
            val = getattr(src, field)
            if field in self.__class__.model_fields and (val is not None or replace_null):
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


class MealieOutModel(MealieModel):
    """
    Base for schemas the API sends back to clients.

    The serializer always emits fields that have defaults, so the serialization JSON schema (and the
    generated TypeScript types) marks them as required instead of optional. Request bodies must keep
    inheriting from MealieModel, or clients would have to send every defaulted field.
    """

    model_config = ConfigDict(json_schema_serialization_defaults_required=True)


class HasUUID(Protocol):
    id: UUID4


def extract_uuids(models: Sequence[HasUUID]) -> list[UUID4]:
    return [x.id for x in models]
