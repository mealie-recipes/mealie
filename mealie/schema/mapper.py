from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
U = TypeVar("U", bound=BaseModel)


def mapper(source: U, dest: T, **_) -> T:
    """
    Map a source model to a destination model. Only top-level fields are mapped.
    """

    for field in source.__fields__:
        if field in dest.__fields__:
            setattr(dest, field, getattr(source, field))

    return dest


def cast(source: U, dest: type[T], **kwargs) -> T:
    create_data = {field: getattr(source, field) for field in source.__fields__ if field in dest.__fields__}
    create_data.update(kwargs or {})
    return dest(**create_data)
