from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
U = TypeVar("U", bound=BaseModel)


def mapper(source: U, dest: T, **_) -> T:
    """
    Map a source model to a destination model. Only top-level fields are mapped.
    """

    for field in source.model_fields:
        if field in dest.model_fields:
            setattr(dest, field, getattr(source, field))

    return dest


def cast(source: U, dest: type[T], **kwargs) -> T:
    create_data = {field: getattr(source, field) for field in source.model_fields if field in dest.model_fields}
    create_data.update(kwargs or {})
    return dest(**create_data)
