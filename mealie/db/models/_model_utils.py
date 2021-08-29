from functools import wraps
from typing import Union

from sqlalchemy.orm import MANYTOMANY, MANYTOONE, ONETOMANY


def handle_one_to_many_list(relation_cls, all_elements: list[dict]):
    elems_to_create = []
    updated_elems = []

    for elem in all_elements:
        elem_id = elem.get("id", None)

        existing_elem = relation_cls.get_ref(match_value=elem_id)

        if existing_elem is None:

            elems_to_create.append(elem)

        else:
            for key, value in elem.items():
                setattr(existing_elem, key, value)

            updated_elems.append(existing_elem)

    new_elems = []
    for elem in elems_to_create:
        new_elems = [relation_cls(**elem) for elem in all_elements]

    return new_elems


def auto_init(exclude: Union[set, list] = None):  # sourcery no-metrics
    """Wraps the `__init__` method of a class to automatically set the common
    attributes.

    Args:
        exclude (Union[set, list], optional): [description]. Defaults to None.
    """

    exclude = exclude or set()
    exclude.add("id")

    def decorator(init):
        @wraps(init)
        def wrapper(self, *args, **kwargs):  # sourcery no-metrics
            """
            Custom initializer that allows nested children initialization.
            Only keys that are present as instance's class attributes are allowed.
            These could be, for example, any mapped columns or relationships.

            Code inspired from GitHub.
            Ref: https://github.com/tiangolo/fastapi/issues/2194
            """
            cls = self.__class__
            model_columns = self.__mapper__.columns
            relationships = self.__mapper__.relationships

            session = kwargs.get("session", None)

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
                    relation_dir = relationships[key].direction.name
                    relation_cls = relationships[key].mapper.entity
                    use_list = relationships[key].uselist

                    if relation_dir == ONETOMANY.name and use_list:
                        instances = handle_one_to_many_list(relation_cls, val)
                        setattr(self, key, instances)

                    if relation_dir == ONETOMANY.name and not use_list:
                        instance = relation_cls(**val)
                        setattr(self, key, instance)

                    elif relation_dir == MANYTOONE.name and not use_list:
                        if isinstance(val, dict):
                            val = val.get("id")

                            if val is None:
                                raise ValueError(f"Expected 'id' to be provided for {key}")

                        if isinstance(val, (str, int)):
                            instance = relation_cls.get_ref(match_value=val, session=session)
                            setattr(self, key, instance)

                    elif relation_dir == MANYTOMANY.name:

                        if not isinstance(val, list):
                            raise ValueError(f"Expected many to many input to be of type list for {key}")

                        if len(val) > 0 and isinstance(val[0], dict):
                            val = [elem.get("id") for elem in val]

                        instances = [x for x in [relation_cls.get_ref(elem, session=session) for elem in val] if x]
                        setattr(self, key, instances)

            return init(self, *args, **kwargs)

        return wrapper

    return decorator
