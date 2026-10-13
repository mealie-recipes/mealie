"""OpenAPI from DRF controller contracts and the retained Pydantic models."""

import inspect
import re
from collections.abc import Callable
from typing import Annotated, Any, get_args, get_origin

from pydantic import TypeAdapter
from pydantic_core import PydanticUndefined

from mealie.core.settings.static import APP_VERSION
from mealie.http.api import APIRoute, Dependency, Parameter
from mealie.http.dependencies import (
    InputField,
    collect_inputs,
    controller_dependencies,
    input_field,
    is_sequence,
    parameters,
)
from mealie.http.description import DESCRIPTION
from mealie.http.encoding import jsonable_encoder
from mealie.http.responses import EventSourceResponse, FileResponse


def generate_schema(routes: list[APIRoute]) -> dict[str, Any]:
    components: dict[str, Any] = {}
    paths: dict[str, Any] = {}

    pending: list[tuple[Any, Any, Any]] = []

    def schema(annotation: Any, mode: str = "validation") -> dict[str, Any]:
        if annotation is inspect.Signature.empty or annotation is None:
            return {}
        if get_origin(annotation) is Annotated:
            args = get_args(annotation)
            metadata = tuple(m for m in args[1:] if not isinstance(m, Parameter | Dependency))
            annotation = Annotated[(args[0], *metadata)] if metadata else args[0]
        index = len(pending)
        pending.append((index, mode, TypeAdapter(annotation)))
        return {"$ref": f"__pending_{index}_{mode}"}

    for route in routes:
        if not route.include_in_schema:
            continue
        path = re.sub(r":path}", "}", route.path)
        fields = collect_inputs(route)
        operation_id = re.sub(r"\W", "_", route.name + path) + "_" + sorted(route.methods)[0].lower()
        query_parameters, body_fields, form_fields = describe_inputs(fields, schema)
        operation: dict[str, Any] = {
            "tags": route.tags,
            "summary": route.summary or route.name.replace("_", " ").title(),
            "responses": {},
        }
        if description := route.description or inspect.getdoc(route.endpoint):
            operation["description"] = description
        if route.deprecated:
            operation["deprecated"] = True
        if query_parameters:
            operation["parameters"] = query_parameters
        if form_fields:
            properties = {f.alias: field_schema(f, schema) for f in form_fields}
            form_schema: dict[str, Any] = {"type": "object", "properties": properties}
            if required := [f.alias for f in form_fields if f.required]:
                form_schema["required"] = required
            media = (
                "multipart/form-data"
                if any(f.source == "file" for f in form_fields)
                else "application/x-www-form-urlencoded"
            )
            body_name = "Body_" + operation_id
            form_schema["title"] = body_name
            components[body_name] = form_schema
            operation["requestBody"] = {
                "content": {media: {"schema": {"$ref": "#/components/schemas/" + body_name}}},
                "required": bool(required),
            }
        elif body_fields:
            if len(body_fields) == 1 and not (body_fields[0].marker and body_fields[0].marker.embed):
                body_schema = schema(body_fields[0].annotation)
            else:
                body_schema = {"type": "object", "properties": {f.alias: field_schema(f, schema) for f in body_fields}}
                if required := [f.alias for f in body_fields if f.required]:
                    body_schema["required"] = required
                body_name = "Body_" + operation_id
                body_schema["title"] = body_name
                components[body_name] = body_schema
                body_schema = {"$ref": "#/components/schemas/" + body_name}
            operation["requestBody"] = {
                "content": {"application/json": {"schema": body_schema}},
                "required": any(f.required for f in body_fields),
            }
        response: dict[str, Any] = {"description": "Successful Response"}
        if route.status_code not in (204, 304) and route.response_class is not FileResponse:
            media = "text/event-stream" if route.response_class is EventSourceResponse else "application/json"
            output_schema = (
                schema(route.response_model, "serialization")
                if route.response_class is not EventSourceResponse
                else {
                    "type": "object",
                    "properties": {
                        "data": {"type": "string"},
                        "event": {"type": "string"},
                        "id": {"type": "string"},
                        "retry": {"type": "integer", "minimum": 0},
                    },
                }
            )
            response["content"] = {media: {"schema": output_schema}}
        operation["responses"][str(route.status_code)] = response
        if fields:
            operation["responses"]["422"] = {
                "description": "Validation Error",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/HTTPValidationError"}}},
            }
        for status, extra in (route.responses or {}).items():
            operation["responses"][str(status)] = {k: v for k, v in extra.items() if k != "model"}
            if "model" in extra:
                operation["responses"][str(status)]["content"] = {
                    "application/json": {"schema": schema(extra["model"], "serialization")}
                }
        if uses_bearer_auth(route):
            operation["security"] = [{"OAuth2PasswordBearer": []}]
        for method in sorted(route.methods):
            item = dict(operation)
            item["operationId"] = re.sub(r"\W", "_", route.name + path) + "_" + method.lower()
            paths.setdefault(path, {})[method.lower()] = item
    components["HTTPValidationError"] = {
        "type": "object",
        "properties": {"detail": {"type": "array", "items": {"$ref": "#/components/schemas/ValidationError"}}},
    }
    components["ValidationError"] = {
        "type": "object",
        "required": ["loc", "msg", "type"],
        "properties": {
            "loc": {"type": "array", "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]}},
            "msg": {"type": "string"},
            "type": {"type": "string"},
            "input": {},
            "ctx": {"type": "object"},
        },
    }
    generated, definitions = TypeAdapter.json_schemas(pending, ref_template="#/components/schemas/{model}")
    components.update(definitions.get("$defs", {}))
    lookup = {f"__pending_{index}_{mode}": value for (index, mode), value in generated.items()}

    def resolve(value: Any) -> Any:
        if isinstance(value, dict):
            if value.get("$ref", "").startswith("__pending_"):
                replacement = lookup[value["$ref"]]
                value = {**replacement, **{k: v for k, v in value.items() if k != "$ref"}}
            return {key: resolve(item) for key, item in value.items() if item is not None}
        if isinstance(value, list):
            return [resolve(item) for item in value]
        return value

    return resolve(
        {
            "openapi": "3.1.0",
            "info": {"title": "Mealie", "description": DESCRIPTION, "version": APP_VERSION},
            "paths": paths,
            "components": {
                "schemas": components,
                "securitySchemes": {
                    "OAuth2PasswordBearer": {
                        "type": "oauth2",
                        "flows": {"password": {"scopes": {}, "tokenUrl": "/api/auth/token"}},
                    }
                },
            },
        }
    )


def uses_bearer_auth(route: APIRoute) -> bool:
    visited: set[Any] = set()

    def visit(target: Any) -> bool:
        if target in visited:
            return False
        visited.add(target)
        if getattr(target, "token_url", None):
            return True
        for param in parameters(target):
            field = input_field(param, set())
            if isinstance(field, Dependency) and visit(field.dependency):
                return True
        if inspect.isclass(target):
            return any(visit(dep.dependency) for _, _, dep in controller_dependencies(target))
        return False

    return (
        any(visit(dep.dependency) for dep in route.dependencies)
        or bool(route.controller and visit(route.controller))
        or visit(route.endpoint)
    )


def field_schema(field: InputField, schema: Callable[..., dict[str, Any]]) -> dict[str, Any]:
    if field.source == "file":
        value: dict[str, Any] = {"type": "string", "contentMediaType": "application/octet-stream"}
        if is_sequence(field.annotation):
            value = {"type": "array", "items": value}
        if type(None) in get_args(field.annotation):
            value = {"anyOf": [value, {"type": "null"}]}
    else:
        value = schema(field.annotation)
    if field.default is not PydanticUndefined and field.default is not None:
        value["default"] = jsonable_encoder(field.default)
    return value


def describe_inputs(
    fields: list[InputField], schema: Callable[..., dict[str, Any]]
) -> tuple[list[Any], list[InputField], list[InputField]]:
    query_parameters: list[Any] = []
    body_fields: list[InputField] = []
    form_fields: list[InputField] = []
    seen = set()
    for field in fields:
        key = field.source, field.alias
        if key in seen:
            continue
        seen.add(key)
        if field.source == "body":
            body_fields.append(field)
        elif field.source in ("form", "file"):
            form_fields.append(field)
        else:
            value_schema = field_schema(field, schema)
            value_schema.setdefault("title", field.alias.replace("_", " ").title())
            query_parameters.append(
                {"name": field.alias, "in": field.source, "required": field.required, "schema": value_schema}
            )
    return query_parameters, body_fields, form_fields
