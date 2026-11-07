from collections.abc import Iterable
from functools import wraps
from typing import TypedDict
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import inspect, select
from sqlalchemy.orm import MANYTOMANY, MANYTOONE, ONETOMANY, Session
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql.base import ColumnCollection

from .._model_base import SqlAlchemyBase
from .helpers import safe_call


def _default_exclusion() -> set[str]:
    return {"id"}


class AutoInitOptions(TypedDict, total=False):
    """Options a model sets as its `model_config` to change how `auto_init` treats it."""

    get_attr: str
    """Attribute to look related rows up by, instead of the primary key."""
    exclude: Iterable[str]
    """Keyword arguments for `auto_init` to skip, because the model's `__init__` handles them."""


class AutoInitConfig(BaseModel):
    """
    Config class for `auto_init` decorator.
    """

    get_attr: str | None = None
    exclude: set = Field(default_factory=_default_exclusion)
    # auto_create: bool = False


def _get_config(relation_cls: type[SqlAlchemyBase], *, protect_primary_key: bool = True) -> AutoInitConfig:
    """
    Returns the config for the given class.

    `protect_primary_key` merges the default `{"id"}` exclusion into the model's own `exclude`.
    """
    cfg = AutoInitConfig()
    options: AutoInitOptions | None = getattr(relation_cls, "model_config", None)
    if not options:
        return cfg

    if "get_attr" in options:
        cfg.get_attr = options["get_attr"]

    if "exclude" in options:
        exclude = set(options["exclude"])
        cfg.exclude = cfg.exclude | exclude if protect_primary_key else exclude

    return cfg


def get_lookup_attr(relation_cls: type[SqlAlchemyBase]) -> str:
    """Returns the primary key attribute of the related class as a string.

    Args:
        relation_cls (DeclarativeMeta): The SQLAlchemy class to get the primary_key from

    Returns:
        Any: [description]
    """

    cfg = _get_config(relation_cls)

    try:
        get_attr = cfg.get_attr
        if get_attr is None:
            get_attr = relation_cls.__table__.primary_key.columns.keys()[0]
    except Exception:
        get_attr = "id"
    return get_attr


# Ownership columns of a related row never come from a nested payload. Moving a row between
# groups or households is not something a payload may do.
_OWNERSHIP_COLUMNS = frozenset({"group_id", "household_id"})


def _is_group_scoped(relation_cls: type[SqlAlchemyBase], group_id) -> bool:
    # Only a real `group_id` column counts. Models such as LongLiveToken proxy `group_id` through
    # their owner; scoping them to the parent's group misses existing rows when that group changes.
    return group_id is not None and "group_id" in inspect(relation_cls).columns


def _lookup_stmt(relation_cls: type[SqlAlchemyBase], lookup_attr: str, value, group_id):
    """Select the related row by `lookup_attr`, limited to `group_id` when the model is group-scoped.

    Without `group_id` (the parent carries no group) the lookup stays unscoped.
    """
    stmt = select(relation_cls).filter_by(**{lookup_attr: value})
    if _is_group_scoped(relation_cls, group_id):
        stmt = stmt.where(relation_cls.group_id == group_id)
    return stmt


def handle_many_to_many(session, get_attr, relation_cls, all_elements: list[dict], group_id=None):
    """
    Proxy call to `handle_one_to_many_list` for many-to-many relationships. Because functionally, they do the same
    """
    return handle_one_to_many_list(session, get_attr, relation_cls, all_elements, group_id)


def handle_one_to_many_list(
    session: Session,
    get_attr,
    relation_cls: type[SqlAlchemyBase],
    all_elements: list[dict] | list[str],
    group_id=None,
):
    elems_to_create: list[dict] = []
    updated_elems: list[dict] = []

    cfg = _get_config(relation_cls)
    scoped = _is_group_scoped(relation_cls, group_id)

    for elem in all_elements:
        elem_id = elem.get(get_attr, None) if isinstance(elem, dict) else elem
        stmt = _lookup_stmt(relation_cls, get_attr, elem_id, group_id)
        existing_elem = session.execute(stmt).scalars().one_or_none()

        if existing_elem is None and isinstance(elem, dict):
            if scoped:
                # A row outside the caller's group is treated as unknown and created in the caller's group.
                # Its primary key is taken, so the new row gets a fresh one.
                elem = {**elem, "group_id": group_id}
                if get_attr == "id" and session.execute(_lookup_stmt(relation_cls, "id", elem_id, None)).first():
                    elem.pop("id")
            elems_to_create.append(elem)
            continue

        elif existing_elem is None:
            continue

        elif isinstance(elem, dict):
            for key, value in elem.items():
                if key not in cfg.exclude and key not in _OWNERSHIP_COLUMNS:
                    setattr(existing_elem, key, value)

        updated_elems.append(existing_elem)

    new_elems = [safe_call(relation_cls, elem.copy(), session=session) for elem in elems_to_create]
    return new_elems + updated_elems


def auto_init():  # sourcery no-metrics
    """Wraps the `__init__` method of a class to automatically set the common
    attributes.

    Args:
        exclude (Union[set, list], optional): [description]. Defaults to None.
    """

    def decorator(init):
        @wraps(init)
        def wrapper(self: SqlAlchemyBase, *args, **kwargs):  # sourcery no-metrics
            """
            Custom initializer that allows nested children initialization.
            Only keys that are present as instance's class attributes are allowed.
            These could be, for example, any mapped columns or relationships.

            Code inspired from GitHub.
            Ref: https://github.com/tiangolo/fastapi/issues/2194
            """
            cls = self.__class__
            config = _get_config(cls, protect_primary_key=not inspect(self).transient)
            exclude = config.exclude

            alchemy_mapper: Mapper = self.__mapper__
            model_columns: ColumnCollection = alchemy_mapper.columns
            relationships = alchemy_mapper.relationships

            session: Session = kwargs.get("session", None)
            group_id = kwargs.get("group_id")

            if session is None:
                raise ValueError("Session is required to initialize the model with `auto_init`")

            for key, val in kwargs.items():
                if key in exclude:
                    continue

                if not hasattr(cls, key):
                    continue
                    # raise TypeError(f"Invalid keyword argument: {key}")

                if key in model_columns:
                    setattr(self, key, val)
                    continue

                if key in relationships:
                    prop: RelationshipProperty = relationships[key]

                    # Identifies the type of relationship (ONETOMANY, MANYTOONE, many-to-one, many-to-many)
                    relation_dir = prop.direction

                    # Identifies the parent class of the related object.
                    relation_cls: type[SqlAlchemyBase] = prop.mapper.entity

                    # Identifies if the relationship was declared with use_list=True
                    use_list: bool = prop.uselist

                    get_attr = get_lookup_attr(relation_cls)

                    if relation_dir == ONETOMANY and use_list:
                        instances = handle_one_to_many_list(session, get_attr, relation_cls, val, group_id)
                        setattr(self, key, instances)

                    elif relation_dir == ONETOMANY:
                        instance = safe_call(relation_cls, val.copy() if val else None, session=session)
                        setattr(self, key, instance)

                    elif relation_dir == MANYTOONE and not use_list:
                        lookup_attr = get_attr
                        if isinstance(val, dict):
                            # Prefer primary key when provided to avoid ambiguous alternate-key lookups
                            if "id" in val and val["id"] is not None:
                                lookup_attr = "id"
                                val = val["id"]
                            else:
                                val = val.get(get_attr)

                            if val is None:
                                raise ValueError(f"Expected '{lookup_attr}' to be provided for {key}")

                        if isinstance(val, str | int | UUID):
                            stmt = _lookup_stmt(relation_cls, lookup_attr, val, group_id)
                            instance = session.execute(stmt).scalars().one_or_none()
                            setattr(self, key, instance)
                        else:
                            # If the value is not of the type defined above we assume that it isn't a valid id
                            # and try a different approach.
                            pass

                    elif relation_dir == MANYTOMANY:
                        instances = handle_many_to_many(session, get_attr, relation_cls, val, group_id)
                        setattr(self, key, instances)

            return init(self, *args, **kwargs)

        return wrapper

    return decorator
