from functools import wraps
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import MANYTOMANY, MANYTOONE, ONETOMANY, Session
from sqlalchemy.orm.mapper import Mapper
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.sql.base import ColumnCollection

from .._model_base import SqlAlchemyBase
from .helpers import safe_call


def _default_exclusion() -> set[str]:
    return {"id"}


class AutoInitConfig(BaseModel):
    """
    Config class for `auto_init` decorator.
    """

    get_attr: str | None = None
    exclude: set = Field(default_factory=_default_exclusion)
    # auto_create: bool = False


def _get_config(relation_cls: type[SqlAlchemyBase]) -> AutoInitConfig:
    """
    Returns the config for the given class.
    """
    cfg = AutoInitConfig()
    cfgKeys = cfg.model_dump().keys()
    # Get the config for the class
    try:
        class_config: ConfigDict = relation_cls.model_config
    except AttributeError:
        return cfg
    # Map all matching attributes in Config to all AutoInitConfig attributes
    for attr in class_config:
        if attr in cfgKeys:
            setattr(cfg, attr, class_config[attr])

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


def handle_many_to_many(session, get_attr, relation_cls, all_elements: list[dict]):
    """
    Proxy call to `handle_one_to_many_list` for many-to-many relationships. Because functionally, they do the same
    """
    return handle_one_to_many_list(session, get_attr, relation_cls, all_elements)


def handle_one_to_many_list(
    session: Session, get_attr, relation_cls: type[SqlAlchemyBase], all_elements: list[dict] | list[str]
):
    elems_to_create: list[dict] = []
    updated_elems: list[dict] = []

    cfg = _get_config(relation_cls)

    for elem in all_elements:
        elem_id = elem.get(get_attr, None) if isinstance(elem, dict) else elem
        stmt = select(relation_cls).filter_by(**{get_attr: elem_id})
        existing_elem = session.execute(stmt).scalars().one_or_none()

        if existing_elem is None and isinstance(elem, dict):
            elems_to_create.append(elem)
            continue

        elif isinstance(elem, dict):
            for key, value in elem.items():
                if key not in cfg.exclude:
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
            config = _get_config(cls)
            exclude = config.exclude

            alchemy_mapper: Mapper = self.__mapper__
            model_columns: ColumnCollection = alchemy_mapper.columns
            relationships = alchemy_mapper.relationships

            session: Session = kwargs.get("session", None)

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
                        instances = handle_one_to_many_list(session, get_attr, relation_cls, val)
                        setattr(self, key, instances)

                    elif relation_dir == ONETOMANY:
                        instance = safe_call(relation_cls, val.copy() if val else None, session=session)
                        setattr(self, key, instance)

                    elif relation_dir == MANYTOONE and not use_list:
                        if isinstance(val, dict):
                            val = val.get(get_attr)

                            if val is None:
                                raise ValueError(f"Expected 'id' to be provided for {key}")

                        if isinstance(val, str | int | UUID):
                            stmt = select(relation_cls).filter_by(**{get_attr: val})
                            instance = session.execute(stmt).scalars().one_or_none()
                            setattr(self, key, instance)
                        else:
                            # If the value is not of the type defined above we assume that it isn't a valid id
                            # and try a different approach.
                            pass

                    elif relation_dir == MANYTOMANY:
                        instances = handle_many_to_many(session, get_attr, relation_cls, val)
                        setattr(self, key, instances)

            return init(self, *args, **kwargs)

        return wrapper

    return decorator
