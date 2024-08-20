from inspect import signature

from fastapi.exceptions import HTTPException, RequestValidationError
from pydantic import ValidationError


def format_exception(ex: Exception) -> str:
    return f"{ex.__class__.__name__}: {ex}"


def make_dependable(cls):
    """
    Pydantic BaseModels are very powerful because we get lots of validations and type checking right out of the box.
    FastAPI can accept a BaseModel as a route Dependency and it will automatically handle things like documentation
    and error handling. However, if we define custom validators then the errors they raise are not handled, leading
    to HTTP 500's being returned.

    To better understand this issue, you can visit https://github.com/tiangolo/fastapi/issues/1474 for context.

    A workaround proposed there adds a classmethod which attempts to init the BaseModel and handles formatting of
    any raised ValidationErrors, custom or otherwise. However, this means essentially duplicating the class's
    signature. This function automates the creation of a workaround method with a matching signature so that you
    can avoid code duplication.

    usage:
    async def fetch(thing_request: ThingRequest = Depends(make_dependable(ThingRequest))):
    """

    def init_cls_and_handle_errors(*args, **kwargs):
        try:
            signature(init_cls_and_handle_errors).bind(*args, **kwargs)
            return cls(*args, **kwargs)
        except (ValidationError, RequestValidationError) as e:
            for error in e.errors():
                error["loc"] = ["query", *list(error["loc"])]
            raise HTTPException(422, detail=[format_exception(ex) for ex in e.errors()]) from None

    init_cls_and_handle_errors.__signature__ = signature(cls)
    return init_cls_and_handle_errors
