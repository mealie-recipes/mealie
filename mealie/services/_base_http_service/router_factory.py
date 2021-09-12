import inspect
from typing import Any, Callable, Optional, Sequence, Type, TypeVar, get_type_hints

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.types import DecoratedCallable
from pydantic import BaseModel

from .base_http_service import BaseHttpService

"""
This code is largely based off of the FastAPI Crud Router
https://github.com/awtkns/fastapi-crudrouter/blob/master/fastapi_crudrouter/core/_base.py
"""

T = TypeVar("T", bound=BaseModel)
S = TypeVar("S", bound=BaseHttpService)
DEPENDENCIES = Optional[Sequence[Depends]]


def get_return(func: Callable, default) -> Type:
    return get_type_hints(func).get("return", default)


def get_func_args(func: Callable) -> Sequence[str]:
    for _, value in get_type_hints(func).items():
        if value:
            return value
        else:
            return None


class RouterFactory(APIRouter):

    schema: Type[T]
    _base_path: str = "/"

    def __init__(self, service: Type[S], prefix: Optional[str] = None, tags: Optional[list[str]] = None, *_, **kwargs):
        """
        RouterFactory takes a concrete service class derived from the BaseHttpService class and returns common
        CRUD Routes for the service. The following features are implmeneted in the RouterFactory:

        1. API endpoint Descriptions are read from the docstrings of the methods in the passed in service class
        2. Return types are inferred from the concrete service schema, or specified from the return type annotations.
        This provides flexibility to return different types based on each route depending on client needs.
        3. Arguemnt types are inferred for Post and Put routes where the first type annotated argument is the data that
        is beging posted or updated. Note that this is only done for the first argument of the method.
        4. The Get and Delete routes assume that you've defined the `write_existing` and `read_existing` methods in the
        service class. The dependencies defined in the `write_existing` and `read_existing` methods are passed directly
        to the FastAPI router and as such should include the `item_id` or equilivent argument.
        """
        self.service: Type[S] = service
        self.schema: Type[T] = service._schema

        prefix = str(prefix or self.schema.__name__).lower()
        prefix = self._base_path + prefix.strip("/")
        tags = tags or [prefix.strip("/").capitalize()]

        super().__init__(prefix=prefix, tags=tags, **kwargs)

        if self.service.get_all:
            self._add_api_route(
                "",
                self._get_all(),
                methods=["GET"],
                response_model=Optional[list[self.schema]],  # type: ignore
                summary="Get All",
                description=inspect.cleandoc(self.service.get_all.__doc__ or ""),
            )

        if self.service.create_one:
            self._add_api_route(
                "",
                self._create(),
                methods=["POST"],
                response_model=self.schema,
                summary="Create One",
                status_code=201,
                description=inspect.cleandoc(self.service.create_one.__doc__ or ""),
            )

        if self.service.update_many:
            self._add_api_route(
                "",
                self._update_many(),
                methods=["PUT"],
                response_model=Optional[list[self.schema]],  # type: ignore
                summary="Update Many",
                description=inspect.cleandoc(self.service.update_many.__doc__ or ""),
            )

        if self.service.delete_all:
            self._add_api_route(
                "",
                self._delete_all(),
                methods=["DELETE"],
                response_model=Optional[list[self.schema]],  # type: ignore
                summary="Delete All",
                description=inspect.cleandoc(self.service.delete_all.__doc__ or ""),
            )

        if self.service.populate_item:
            self._add_api_route(
                "/{item_id}",
                self._get_one(),
                methods=["GET"],
                response_model=get_type_hints(self.service.populate_item).get("return", self.schema),
                summary="Get One",
                description=inspect.cleandoc(self.service.populate_item.__doc__ or ""),
            )

        if self.service.update_one:
            self._add_api_route(
                "/{item_id}",
                self._update(),
                methods=["PUT"],
                response_model=self.schema,
                summary="Update One",
                description=inspect.cleandoc(self.service.update_one.__doc__ or ""),
            )

        if self.service.delete_one:
            self._add_api_route(
                "/{item_id}",
                self._delete_one(),
                methods=["DELETE"],
                response_model=self.schema,
                summary="Delete One",
                description=inspect.cleandoc(self.service.delete_one.__doc__ or ""),
            )

    def _add_api_route(self, path: str, endpoint: Callable[..., Any], **kwargs: Any) -> None:
        dependencies = []
        super().add_api_route(path, endpoint, dependencies=dependencies, **kwargs)

    def api_route(self, path: str, *args: Any, **kwargs: Any) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """Overrides and exiting route if it exists"""
        methods = kwargs["methods"] if "methods" in kwargs else ["GET"]
        self.remove_api_route(path, methods)
        return super().api_route(path, *args, **kwargs)

    def get(self, path: str, *args: Any, **kwargs: Any) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["Get"])
        return super().get(path, *args, **kwargs)

    def post(self, path: str, *args: Any, **kwargs: Any) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["POST"])
        return super().post(path, *args, **kwargs)

    def put(self, path: str, *args: Any, **kwargs: Any) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["PUT"])
        return super().put(path, *args, **kwargs)

    def delete(self, path: str, *args: Any, **kwargs: Any) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["DELETE"])
        return super().delete(path, *args, **kwargs)

    def remove_api_route(self, path: str, methods: list[str]) -> None:
        methods_ = set(methods)

        for route in self.routes:
            if route.path == f"{self.prefix}{path}" and route.methods == methods_:
                self.routes.remove(route)

    def _get_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        def route(service: S = Depends(self.service.private)) -> T:  # type: ignore
            return service.get_all()

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        def route(service: S = Depends(self.service.write_existing)) -> T:  # type: ignore
            return service.item

        return route

    def _create(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        create_schema = get_func_args(self.service.create_one) or self.schema

        def route(data: create_schema, service: S = Depends(self.service.private)) -> T:  # type: ignore
            return service.create_one(data)

        return route

    def _update(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        update_schema = get_func_args(self.service.update_one) or self.schema

        def route(data: update_schema, service: S = Depends(self.service.write_existing)) -> T:  # type: ignore
            return service.update_one(data)

        return route

    def _update_many(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        update_many_schema = get_func_args(self.service.update_many) or list[self.schema]

        def route(data: update_many_schema, service: S = Depends(self.service.private)) -> T:  # type: ignore
            return service.update_many(data)

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        def route(service: S = Depends(self.service.write_existing)) -> T:  # type: ignore
            return service.delete_one()

        return route

    def _delete_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        raise NotImplementedError

    @staticmethod
    def get_routes() -> list[str]:
        return ["get_all", "create", "delete_all", "get_one", "update", "delete_one"]
