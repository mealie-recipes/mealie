"""Bind Mealie controllers to declarative DRF routes."""

import inspect
from collections.abc import Callable
from typing import Any

from mealie.http.api import APIRouter

RETURN_TYPES_FUNC_KEY = "__return_types_func__"


def controller[T](router: APIRouter, *urls: str) -> Callable[[type[T]], type[T]]:
    def decorate(cls: type[T]) -> type[T]:
        members = dict(inspect.getmembers(cls, inspect.isfunction))
        for url in urls:
            for name in ("get", "post", "put", "patch", "delete"):
                if name not in members:
                    continue
                func = members[name]
                if any(route.endpoint is func and route.path == router.prefix + url for route in router.routes):
                    continue
                options: dict[str, Any] = {"response_model": None}
                if return_types := getattr(func, RETURN_TYPES_FUNC_KEY, None):
                    model, status, responses, kwargs = return_types()
                    options.update(response_model=model, status_code=status, responses=responses, **kwargs)
                router.api_route(url, methods=[name.upper()], **options)(func)
        for route in router.routes:
            if route.endpoint in members.values() and route.controller is None:
                route.controller = cls
        # Private annotations were initialized by the old CBV binding helper.
        from typing import get_type_hints

        for name in get_type_hints(cls):
            if name.startswith("_") and not hasattr(cls, name):
                setattr(cls, name, None)
        return cls

    return decorate
