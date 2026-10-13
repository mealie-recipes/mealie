"""Request-scoped controller dependencies and Pydantic input validation."""

import asyncio
import inspect
import types
from contextlib import AsyncExitStack
from dataclasses import dataclass
from typing import Annotated, Any, get_args, get_origin, get_type_hints

from pydantic import BaseModel, TypeAdapter, ValidationError
from pydantic_core import PydanticUndefined

from mealie.http.api import APIRoute, Dependency, Parameter, RequestValidationError
from mealie.http.requests import Request
from mealie.http.responses import BackgroundTasks, Response, UploadFile

# Test overrides and embedded callers use the same request lifetime as production.
dependency_overrides: dict[Any, Any] = {}


def strip_annotated(annotation: Any) -> Any:
    return get_args(annotation)[0] if get_origin(annotation) is Annotated else annotation


def is_model(annotation: Any) -> bool:
    return inspect.isclass(annotation) and issubclass(annotation, BaseModel)


def is_complex(annotation: Any) -> bool:
    annotation = strip_annotated(annotation)
    origin = get_origin(annotation)
    if origin in (types.UnionType, __import__("typing").Union):
        return any(is_complex(arg) for arg in get_args(annotation) if arg is not type(None))
    return is_model(annotation) or origin in (list, dict, set, tuple) or annotation in (list, dict, set, tuple)


def is_sequence(annotation: Any) -> bool:
    annotation = strip_annotated(annotation)
    if get_origin(annotation) in (types.UnionType, __import__("typing").Union):
        return any(is_sequence(arg) for arg in get_args(annotation))
    return get_origin(annotation) in (list, set, tuple) or annotation in (list, set, tuple)


def signature(target: Any) -> inspect.Signature:
    return inspect.signature(target)


def parameters(target: Any) -> list[inspect.Parameter]:
    sig = signature(target)
    return [
        p
        for p in sig.parameters.values()
        if p.name not in ("self", "cls")
        and p.kind
        not in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        )
    ]


def controller_dependencies(cls: type[Any]) -> list[tuple[str, Any, Dependency]]:
    return [
        (name, annotation, default)
        for name, annotation in get_type_hints(cls, include_extras=True).items()
        if isinstance(default := getattr(cls, name, None), Dependency)
    ]


@dataclass
class InputField:
    name: str
    annotation: Any
    source: str
    alias: str
    default: Any = PydanticUndefined
    marker: Parameter | None = None

    @property
    def required(self) -> bool:
        return self.source == "path" or (
            self.default is PydanticUndefined and not (self.marker and self.marker.default_factory)
        )


def input_field(param: inspect.Parameter, path_names: set[str]) -> InputField | Dependency | type[Any]:
    annotation = param.annotation if param.annotation is not inspect.Parameter.empty else Any
    default = param.default
    metadata = get_args(annotation)[1:] if get_origin(annotation) is Annotated else ()
    marker = next((m for m in metadata if isinstance(m, Parameter | Dependency)), None)
    if isinstance(default, Parameter | Dependency):
        marker = default
    if isinstance(marker, Dependency):
        return Dependency(marker.dependency or strip_annotated(annotation), marker.use_cache)
    base = strip_annotated(annotation)
    if base in (Request, Response, BackgroundTasks):
        return base
    if isinstance(marker, Parameter):
        default = marker.default
        if (
            default is PydanticUndefined
            and param.default is not inspect.Parameter.empty
            and not isinstance(param.default, Parameter)
        ):
            default = param.default
        source = marker.source
    else:
        source = "path" if param.name in path_names else "body" if is_complex(annotation) else "query"
        default = PydanticUndefined if default is inspect.Parameter.empty else default
    alias = marker.alias if isinstance(marker, Parameter) and marker.alias else param.name
    if source == "header" and not (marker and marker.alias):
        alias = alias.replace("_", "-")
    return InputField(param.name, annotation, source, alias, default, marker)


def collect_inputs(route: APIRoute) -> list[InputField]:
    import re

    fields: list[InputField] = []
    visited: set[Any] = set()
    path_names = set(re.findall(r"{([^}:]+)(?::[^}]+)?}", route.path))

    def visit(target: Any) -> None:
        if target in visited:
            return
        visited.add(target)
        for param in parameters(target):
            field = input_field(param, path_names)
            if isinstance(field, Dependency):
                visit(field.dependency)
            elif isinstance(field, InputField):
                fields.append(field)
        if inspect.isclass(target) and not is_model(target):
            for _, _, dep in controller_dependencies(target):
                visit(dep.dependency)

    for dependency in route.dependencies:
        visit(dependency.dependency)
    if route.controller:
        visit(route.controller)
    visit(route.endpoint)
    return fields


class RequestContext:
    def __init__(self, request: Request, route: APIRoute, path_params: dict[str, Any]) -> None:
        self.request, self.route, self.path_params = request, route, path_params
        self.response = Response()
        self.background = BackgroundTasks()
        self.cache: dict[Any, Any] = {}
        self.stack = AsyncExitStack()
        self.inputs = collect_inputs(route)
        self.body_fields = [f for f in self.inputs if f.source == "body"]
        self.form_fields = [f for f in self.inputs if f.source in ("form", "file")]
        self.closed = False
        self.finished = False

    async def close(self) -> None:
        if not self.closed:
            self.closed = True
            await self.stack.aclose()

    async def finish(self) -> None:
        if self.finished:
            return
        self.finished = True
        try:
            await self.background.run_async()
        finally:
            await self.close()

    async def resolve(self, target: Any, use_cache: bool = True) -> Any:
        original = target
        if use_cache and original in self.cache:
            return self.cache[original]
        target = dependency_overrides.get(target, target)
        kwargs = await self.arguments(target)
        if inspect.isclass(target) and not is_model(target):
            for name, _, dependency in controller_dependencies(target):
                kwargs[name] = await self.resolve(dependency.dependency, dependency.use_cache)
            # Dependencies are attributes on controller instances, not constructor parameters.
            attributes = {name: kwargs.pop(name) for name, _, _ in controller_dependencies(target)}
            result = await asyncio.to_thread(target, **kwargs)
            for name, value in attributes.items():
                setattr(result, name, value)
        elif inspect.isasyncgenfunction(target):
            from contextlib import asynccontextmanager

            result = await self.stack.enter_async_context(asynccontextmanager(target)(**kwargs))
        elif inspect.isgeneratorfunction(target):
            from contextlib import contextmanager

            result = self.stack.enter_context(contextmanager(target)(**kwargs))
        else:
            result = (
                target(**kwargs) if inspect.iscoroutinefunction(target) else await asyncio.to_thread(target, **kwargs)
            )
            if inspect.isawaitable(result):
                result = await result
        if use_cache:
            self.cache[original] = result
        return result

    async def arguments(self, target: Any) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}
        errors: list[dict[str, Any]] = []
        for param in parameters(target):
            field = input_field(param, set(self.path_params))
            if isinstance(field, Dependency):
                kwargs[param.name] = await self.resolve(field.dependency, field.use_cache)
            elif field is Request:
                kwargs[param.name] = self.request
            elif field is Response:
                kwargs[param.name] = self.response
            elif field is BackgroundTasks:
                kwargs[param.name] = self.background
            else:
                assert isinstance(field, InputField)
                try:
                    kwargs[param.name] = self.read_input(field)
                except RequestValidationError as exc:
                    errors.extend(exc.errors())
        if errors:
            raise RequestValidationError(errors)
        return kwargs

    @property
    def content_type(self) -> str:
        return self.request.drf.content_type.split(";", 1)[0].strip().lower()

    @property
    def body_data(self) -> Any:
        media = self.content_type
        if not media or media == "application/json" or media.startswith("application/") and media.endswith("+json"):
            return self.request.drf.data
        return self.request.drf.body

    @property
    def form_data(self) -> Any:
        if self.content_type in ("application/x-www-form-urlencoded", "multipart/form-data"):
            return self.request.drf.data
        return {}

    def parse_body(self) -> None:
        # Parsing errors historically precede authentication; model validation
        # follows the authentication dependencies.
        if self.body_fields:
            _ = self.body_data
        elif self.form_fields:
            _ = self.form_data

    def read_input(self, field: InputField) -> Any:
        source, alias = field.source, field.alias
        location: tuple[Any, ...] = ("body" if source in ("file", "form") else source, alias)
        if source == "path":
            value = self.path_params.get(alias, PydanticUndefined)
        elif source in ("query", "header", "cookie"):
            mapping = {
                "query": self.request.query_params,
                "header": self.request.headers,
                "cookie": self.request.cookies,
            }[source]
            value = mapping.get(alias, PydanticUndefined)
            if source == "query" and is_sequence(field.annotation) and alias in mapping:
                value = mapping.getlist(alias)
        elif source == "body":
            value = self.body_data
            embed = len(self.body_fields) > 1 or bool(field.marker and field.marker.embed)
            if embed:
                value = value.get(alias, PydanticUndefined) if isinstance(value, dict) else PydanticUndefined
            else:
                location = ("body",)
                if self.request.drf.META.get("CONTENT_LENGTH", "0") in ("", "0"):
                    value = PydanticUndefined
        else:
            mapping = self.form_data
            value = mapping.get(alias, PydanticUndefined)
            if is_sequence(field.annotation) and alias in mapping:
                value = mapping.getlist(alias)
            if source in ("form", "file") and value == "":
                value = PydanticUndefined
            if source == "file" and value is not PydanticUndefined:

                def upload(item: Any) -> Any:
                    from django.core.files.uploadedfile import UploadedFile

                    if strip_annotated(field.annotation) is bytes:
                        return item.read() if isinstance(item, UploadedFile) else item
                    if not isinstance(item, UploadedFile):
                        error = ValueError(f"Expected UploadFile, received: {type(item)}")
                        raise RequestValidationError(
                            [
                                {
                                    "type": "value_error",
                                    "loc": location,
                                    "msg": f"Value error, {error}",
                                    "input": item,
                                    "ctx": {"error": error},
                                }
                            ]
                        )
                    return UploadFile(item.file, item.name, {"content-type": item.content_type}, item.size)

                value = [upload(v) for v in value] if isinstance(value, list) else upload(value)
        if value is PydanticUndefined or value is None:
            if field.marker and field.marker.default_factory:
                return field.marker.default_factory()
            if field.default is not PydanticUndefined:
                return field.default
            raise RequestValidationError([{"type": "missing", "loc": location, "msg": "Field required", "input": None}])
        if source == "file" and strip_annotated(field.annotation) is not bytes:
            return value
        annotation = field.annotation
        # Remove our HTTP marker; keep Pydantic constraints (e.g. UUID4).
        if get_origin(annotation) is Annotated:
            args = get_args(annotation)
            metadata = tuple(m for m in args[1:] if not isinstance(m, Parameter | Dependency))
            annotation = Annotated[(args[0], *metadata)] if metadata else args[0]
        if field.marker:
            annotation = Annotated[annotation, field.marker.validation_field()]
        try:
            return TypeAdapter(annotation).validate_python(value)
        except ValidationError as exc:
            raise RequestValidationError(
                [{**error, "loc": (*location, *error["loc"])} for error in exc.errors(include_url=False)]
            ) from exc

    async def execute(self) -> Any:
        for dependency in self.route.dependencies:
            await self.resolve(dependency.dependency, dependency.use_cache)
        endpoint = self.route.endpoint
        if self.route.controller:
            instance = await self.resolve(self.route.controller)
            endpoint = getattr(instance, endpoint.__name__)
        kwargs = await self.arguments(endpoint)
        if inspect.iscoroutinefunction(endpoint) or inspect.isasyncgenfunction(endpoint):
            result = endpoint(**kwargs)
        else:
            result = await asyncio.to_thread(endpoint, **kwargs)
        if inspect.isawaitable(result):
            result = await result
        return result
