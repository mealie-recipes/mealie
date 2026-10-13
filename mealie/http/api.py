"""Declarative HTTP contracts shared by DRF views and API documentation.

These markers describe existing Mealie controller signatures. They do not
install another ASGI application or depend on FastAPI's dependency resolver.
"""

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from http import HTTPStatus
from typing import Any

from pydantic import Field
from pydantic_core import PydanticUndefined
from rest_framework import status as status

from mealie.http.requests import Request as Request
from mealie.http.responses import BackgroundTasks as BackgroundTasks
from mealie.http.responses import Response as Response
from mealie.http.responses import UploadFile as UploadFile

# Existing callers use the newer HTTP status name.
status.HTTP_422_UNPROCESSABLE_CONTENT = 422


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: Any = None, headers: dict[str, str] | None = None) -> None:
        self.status_code = status_code
        self.detail = detail if detail is not None else HTTPStatus(status_code).phrase
        self.headers = headers or {}
        super().__init__(self.detail)


class RequestValidationError(Exception):
    def __init__(self, errors: list[dict[str, Any]], body: Any = None) -> None:
        self._errors = errors
        self.body = body
        self.endpoint_ctx: dict[str, Any] = {}
        super().__init__(str(errors))

    def errors(self) -> list[dict[str, Any]]:
        return self._errors

    def __str__(self) -> str:
        message = f"{len(self._errors)} validation error{'s' if len(self._errors) != 1 else ''}:\n"
        message += "".join(f"  {error}\n" for error in self._errors)
        context = self.endpoint_ctx
        if all(context.get(key) for key in ("file", "line", "function")):
            message += f'\n  File "{context["file"]}", line {context["line"]}, in {context["function"]}'
            message += f"\n    {context['path']}"
        return message.rstrip()


@dataclass(frozen=True)
class Dependency:
    dependency: Callable[..., Any] | None = None
    use_cache: bool = True


class Parameter:
    source = "query"

    def __init__(
        self,
        default: Any = PydanticUndefined,
        *,
        alias: str | None = None,
        embed: bool = False,
        default_factory: Callable[..., Any] | None = None,
        **constraints: Any,
    ) -> None:
        self.default = PydanticUndefined if default is Ellipsis else default
        self.alias = alias
        self.embed = embed
        self.default_factory = default_factory
        self.constraints = constraints

    def validation_field(self) -> Any:
        return Field(
            **{
                k: v
                for k, v in self.constraints.items()
                if k
                in {
                    "gt",
                    "ge",
                    "lt",
                    "le",
                    "min_length",
                    "max_length",
                    "pattern",
                    "multiple_of",
                    "strict",
                }
            }
        )


class QueryParameter(Parameter):
    source = "query"


class PathParameter(Parameter):
    source = "path"


class BodyParameter(Parameter):
    source = "body"


class FormParameter(Parameter):
    source = "form"


class FileParameter(FormParameter):
    source = "file"


class HeaderParameter(Parameter):
    source = "header"


class CookieParameter(Parameter):
    source = "cookie"


# Marker factories deliberately return Any: annotated parameters hold an injected
# value at runtime, while their defaults describe how HTTP should supply it.
def Depends(dependency: Callable[..., Any] | None = None, *, use_cache: bool = True) -> Any:
    return Dependency(dependency, use_cache)


def Query(*args: Any, **kwargs: Any) -> Any:
    return QueryParameter(*args, **kwargs)


def Path(*args: Any, **kwargs: Any) -> Any:
    return PathParameter(*args, **kwargs)


def Body(*args: Any, **kwargs: Any) -> Any:
    return BodyParameter(*args, **kwargs)


def Form(*args: Any, **kwargs: Any) -> Any:
    return FormParameter(*args, **kwargs)


def File(*args: Any, **kwargs: Any) -> Any:
    return FileParameter(*args, **kwargs)


def Header(*args: Any, **kwargs: Any) -> Any:
    return HeaderParameter(*args, **kwargs)


def Cookie(*args: Any, **kwargs: Any) -> Any:
    return CookieParameter(*args, **kwargs)


INFER = object()


@dataclass
class APIRoute:
    path: str
    endpoint: Callable[..., Any]
    methods: set[str]
    name: str
    tags: list[Any] = field(default_factory=list)
    dependencies: list[Dependency] = field(default_factory=list)
    response_model: Any = None
    response_class: Any = None
    status_code: int = 200
    include_in_schema: bool = True
    deprecated: bool = False
    summary: str | None = None
    description: str | None = None
    responses: dict[Any, Any] | None = None
    controller: type[Any] | None = None
    route_class: type[Any] | None = None
    options: dict[str, Any] = field(default_factory=dict)


class APIRouter:
    def __init__(
        self,
        *,
        prefix: str = "",
        tags: list[Any] | None = None,
        dependencies: list[Dependency] | None = None,
        route_class: type[Any] | None = None,
        include_in_schema: bool = True,
        **kwargs: Any,
    ) -> None:
        self.prefix = prefix
        self.tags = tags or []
        self.dependencies = dependencies or []
        self.route_class = route_class
        self.include_in_schema = include_in_schema
        self.routes: list[APIRoute] = []

    def api_route(self, path: str, *, methods: list[str], **kwargs: Any) -> Callable:
        def register(endpoint: Callable) -> Callable:
            options = dict(kwargs)
            model = options.pop("response_model", INFER)
            if model is INFER:
                model = inspect.signature(endpoint).return_annotation
                if model is inspect.Signature.empty or model is None:
                    model = None
            route = APIRoute(
                path=self.prefix + path,
                endpoint=endpoint,
                methods={m.upper() for m in methods},
                name=options.pop("name", endpoint.__name__),
                tags=list(dict.fromkeys(self.tags + options.pop("tags", []))),
                dependencies=self.dependencies + options.pop("dependencies", []),
                response_model=model,
                response_class=options.pop("response_class", None),
                status_code=options.pop("status_code", 200),
                include_in_schema=self.include_in_schema and options.pop("include_in_schema", True),
                deprecated=options.pop("deprecated", False),
                summary=options.pop("summary", None),
                description=options.pop("description", None),
                responses=options.pop("responses", None),
                route_class=self.route_class,
                options=options,
            )
            self.routes.append(route)
            return endpoint

        return register

    def get(self, path: str, **kwargs: Any) -> Callable:
        return self.api_route(path, methods=["GET"], **kwargs)

    def post(self, path: str, **kwargs: Any) -> Callable:
        return self.api_route(path, methods=["POST"], **kwargs)

    def put(self, path: str, **kwargs: Any) -> Callable:
        return self.api_route(path, methods=["PUT"], **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Callable:
        return self.api_route(path, methods=["PATCH"], **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Callable:
        return self.api_route(path, methods=["DELETE"], **kwargs)

    def include_router(self, router: APIRouter, *, prefix: str = "", **kwargs: Any) -> None:
        for route in router.routes:
            self.routes.append(
                replace(
                    route,
                    path=self.prefix + prefix + route.path,
                    tags=list(dict.fromkeys(self.tags + kwargs.get("tags", []) + route.tags)),
                    dependencies=self.dependencies + kwargs.get("dependencies", []) + route.dependencies,
                    include_in_schema=self.include_in_schema
                    and route.include_in_schema
                    and kwargs.get("include_in_schema", True),
                )
            )

    def url_path_for(self, name: str, **params: Any) -> str:
        route = next(r for r in self.routes if r.name == name)
        result = route.path
        for key, value in params.items():
            result = result.replace("{" + key + "}", str(value))
        return result
