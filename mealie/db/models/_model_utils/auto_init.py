from __future__ import annotations

from functools import wraps

from pydantic import BaseModel, Field
from sqlalchemy.orm import MANYTOMANY, MANYTOONE, ONETOMANY, Session
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql.base import ColumnCollection
from sqlalchemy.util._collections import ImmutableProperties

from .helpers import safe_call


def _default_exclusion() -> set[str]:
    return {"id"}


class AutoInitConfig(BaseModel):
    """
    Config class for `auto_init` decorator.
    """

    get_attr: str = None
    exclude: set = Field(default_factory=_default_exclusion)
    # auto_create: bool = False


def _get_config(relation_cls: DeclarativeMeta) -> AutoInitConfig:
    """
    Returns the config for the given class.
    """
    cfg = AutoInitConfig()
    cfgKeys = cfg.dict().keys()
    # Get the config for the class
    try:
        class_config: AutoInitConfig = relation_cls.Config
    except AttributeError:
        return cfg
    # Map all matching attributes in Config to all AutoInitConfig attributes
    for attr in dir(class_config):
        if attr in cfgKeys:
            setattr(cfg, attr, getattr(class_config, attr))

    return cfg


def get_lookup_attr(relation_cls: DeclarativeMeta) -> str:
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


def handle_many_to_many(session, get_attr, relation_cls, all_elements: list[dict]):
    """
    Proxy call to `handle_one_to_many_list` for many-to-many relationships. Because functionally, they do the same
    """
    return handle_one_to_many_list(session, get_attr, relation_cls, all_elements)


def handle_one_to_many_list(session: Session, get_attr, relation_cls, all_elements: list[dict] | list[str]):
    elems_to_create: list[dict] = []
    updated_elems: list[dict] = []

    cfg = _get_config(relation_cls)

    for elem in all_elements:
        elem_id = elem.get(get_attr, None) if isinstance(elem, dict) else elem
        existing_elem = session.query(relation_cls).filter_by(**{get_attr: elem_id}).one_or_none()

        if existing_elem is None:
            elems_to_create.append(elem)
            continue

        elif isinstance(elem, dict):
            for key, value in elem.items():
                if key not in cfg.exclude:
                    setattr(existing_elem, key, value)

        updated_elems.append(existing_elem)

    new_elems = [safe_call(relation_cls, elem, session=session) for elem in elems_to_create]
    return new_elems + updated_elems


def auto_init():  # sourcery no-metrics
    """Wraps the `__init__` method of a class to automatically set the common
    attributes.

    Args:
        exclude (Union[set, list], optional): [description]. Defaults to None.
    """

    def decorator(init):
        @wraps(init)
        def wrapper(self: DeclarativeMeta, *args, **kwargs):  # sourcery no-metrics
            """
            Custom initializer that allows nested children initialization.
            Only keys that are present as instance's class attributes are allowed.
            These could be, for example, any mapped columns or relationships.

            Code inspired from GitHub.
            Ref: https://github.com/tiangolo/fastapi/issues/2194
            """
            cls = self.__class__

            exclude = _get_config(cls).exclude

            alchemy_mapper: Mapper = self.__mapper__
            model_columns: ColumnCollection = alchemy_mapper.columns
            relationships: ImmutableProperties = alchemy_mapper.relationships

            session = kwargs.get("session", None)

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
                    relation_cls: DeclarativeMeta = prop.mapper.entity

                    # Identifies if the relationship was declared with use_list=True
                    use_list: bool = prop.uselist

                    get_attr = get_lookup_attr(relation_cls)

                    if relation_dir == ONETOMANY and use_list:
                        instances = handle_one_to_many_list(session, get_attr, relation_cls, val)
                        setattr(self, key, instances)

                    elif relation_dir == ONETOMANY:
                        instance = safe_call(relation_cls, val, session=session)
                        setattr(self, key, instance)

                    elif relation_dir == MANYTOONE and not use_list:
                        if isinstance(val, dict):
                            val = val.get(get_attr)

                            if val is None:
                                raise ValueError(f"Expected 'id' to be provided for {key}")

                        if isinstance(val, (str, int)):
                            instance = session.query(relation_cls).filter_by(**{get_attr: val}).one_or_none()
                            setattr(self, key, instance)

                    elif relation_dir == MANYTOMANY:
                        instances = handle_many_to_many(session, get_attr, relation_cls, val)
                        setattr(self, key, instances)

            return init(self, *args, **kwargs)

        return wrapper

    return decorator
