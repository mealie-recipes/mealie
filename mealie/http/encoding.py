from collections.abc import Mapping
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any

from pydantic import BaseModel
from pydantic_core import to_jsonable_python


def jsonable_encoder(
    obj: Any,
    *,
    include: Any = None,
    exclude: Any = None,
    by_alias: bool = True,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    **kwargs: Any,
) -> Any:
    if isinstance(obj, BaseModel):
        return obj.model_dump(
            mode="json",
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
    if isinstance(obj, Mapping):
        return {
            str(k): jsonable_encoder(v, by_alias=by_alias, exclude_none=exclude_none)
            for k, v in obj.items()
            if not str(k).startswith("_sa")
            and (include is None or k in include)
            and (exclude is None or k not in exclude)
            and (not exclude_none or v is not None)
        }
    if isinstance(obj, list | tuple | set | frozenset):
        return [jsonable_encoder(v, by_alias=by_alias, exclude_none=exclude_none) for v in obj]
    if isinstance(obj, datetime | date | time):
        return obj.isoformat()
    if isinstance(obj, timedelta):
        return obj.total_seconds()
    if isinstance(obj, Decimal):
        exponent = obj.as_tuple().exponent
        return int(obj) if isinstance(exponent, int) and exponent >= 0 else float(obj)
    return to_jsonable_python(obj, fallback=lambda value: jsonable_encoder(vars(value)))
