from typing import Any, Callable, Optional, Sequence, Type, TypeVar

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.types import DecoratedCallable
from pydantic import BaseModel

from .base_http_service import BaseHttpService

""""
This code is largely based off of the FastAPI Crud Router
https://github.com/awtkns/fastapi-crudrouter/blob/master/fastapi_crudrouter/core/_base.py
"""

T = TypeVar("T", bound=BaseModel)
S = TypeVar("S", bound=BaseHttpService)
DEPENDENCIES = Optional[Sequence[Depends]]


class RouterFactory(APIRouter):
    schema: Type[T]
    create_schema: Type[T]
    update_schema: Type[T]
    _base_path: str = "/"

    def __init__(
        self,
        service: Type[S],
        prefix: Optional[str] = None,
        tags: Optional[list[str]] = None,
        *args,
        **kwargs,
    ):

        self.service: Type[S] = service
        self.schema: Type[T] = service._schema

        # HACK: Special Case for Coobooks, not sure this is a good way to handle the abstraction :/
        if hasattr(self.service, "_get_one_schema"):
            self.get_one_schema = self.service._get_one_schema
        else:
            self.get_one_schema = self.schema

        self.update_schema: Type[T] = service._update_schema
        self.create_schema: Type[T] = service._create_schema

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
            )

        if self.service.create_one:
            self._add_api_route(
                "",
                self._create(),
                methods=["POST"],
                response_model=self.schema,
                summary="Create One",
            )

        if self.service.update_many:
            self._add_api_route(
                "",
                self._update_many(),
                methods=["PUT"],
                response_model=Optional[list[self.schema]],  # type: ignore
                summary="Update Many",
            )

        if self.service.delete_all:
            self._add_api_route(
                "",
                self._delete_all(),
                methods=["DELETE"],
                response_model=Optional[list[self.schema]],  # type: ignore
                summary="Delete All",
            )

        if self.service.populate_item:
            self._add_api_route(
                "/{item_id}",
                self._get_one(),
                methods=["GET"],
                response_model=self.get_one_schema,
                summary="Get One",
            )

        if self.service.update_one:
            self._add_api_route(
                "/{item_id}",
                self._update(),
                methods=["PUT"],
                response_model=self.schema,
                summary="Update One",
            )

        if self.service.delete_one:
            self._add_api_route(
                "/{item_id}",
                self._delete_one(),
                methods=["DELETE"],
                response_model=self.schema,
                summary="Delete One",
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
        def route(data: self.create_schema, service: S = Depends(self.service.private)) -> T:  # type: ignore
            return service.create_one(data)

        return route

    def _update(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        def route(data: self.update_schema, service: S = Depends(self.service.write_existing)) -> T:  # type: ignore
            return service.update_one(data)

        return route

    def _update_many(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        def route(data: list[self.update_schema], service: S = Depends(self.service.write_existing)) -> T:  # type: ignore
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
