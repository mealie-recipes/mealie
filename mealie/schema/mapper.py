from pydantic import BaseModel


def mapper[U: BaseModel, T: BaseModel](source: U, dest: T, **_) -> T:
    """
    Map a source model to a destination model. Only top-level fields are mapped.
    """

    for field in source.__class__.model_fields:
        if field in dest.__class__.model_fields:
            setattr(dest, field, getattr(source, field))

    return dest


def cast[U: BaseModel, T: BaseModel](source: U, dest: type[T], **kwargs) -> T:
    create_data = {
        field: getattr(source, field) for field in source.__class__.model_fields if field in dest.model_fields
    }
    create_data.update(kwargs or {})
    return dest(**create_data)
