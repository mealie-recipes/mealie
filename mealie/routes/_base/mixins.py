from __future__ import annotations

from logging import Logger
from typing import Callable, Type

from fastapi import HTTPException, status

from mealie.repos.repository_generic import RepositoryGeneric
from mealie.schema.response import ErrorResponse


class CrudMixins:
    repo: RepositoryGeneric
    exception_msgs: Callable[[Type[Exception]], str] | None
    default_message: str = "An unexpected error occurred."

    def __init__(
        self,
        repo: RepositoryGeneric,
        logger: Logger,
        exception_msgs: Callable[[Type[Exception]], str] = None,
        default_message: str = None,
    ) -> None:
        """
        The CrudMixins class is a mixin class that provides a common set of methods for CRUD operations.
        This class is inteded to be used in a composition pattern where a class has a mixin property. For example:

        ```
        class MyClass:
            def __init(self repo, logger):
                self.mixins = CrudMixins(repo, logger)
        ```

        """
        self.repo = repo
        self.logger = logger
        self.exception_msgs = exception_msgs

        if default_message:
            self.default_message = default_message

    def set_default_message(self, default_msg: str) -> "CrudMixins":
        """
        Use this method to set a lookup function for exception messages. When an exception is raised, and
        no custom message is set, the default message will be used.

        IMPORTANT! The function returns the same instance of the CrudMixins class, so you can chain calls.
        """
        self.default_msg = default_msg
        return self

    def get_exception_message(self, ext: Exception) -> str:
        if self.exception_msgs:
            return self.exception_msgs(type(ext))
        return self.default_message

    def handle_exception(self, ex: Exception) -> None:
        # Cleanup
        self.logger.exception(ex)
        self.repo.session.rollback()

        # Respond
        msg = self.get_exception_message(ex)

        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse.respond(message=msg, exception=str(ex)),
        )

    def create_one(self, data):
        item = None
        try:
            item = self.repo.create(data)
        except Exception as ex:
            self.handle_exception(ex)

        return item

    def update_one(self, data, item_id):
        item = self.repo.get(item_id)

        if not item:
            return

        try:
            item = self.repo.update(item.id, data)  # type: ignore
        except Exception as ex:
            self.handle_exception(ex)

        return item

    def patch_one(self, data, item_id) -> None:
        self.repo.get(item_id)

        try:
            self.repo.patch(item_id, data.dict(exclude_unset=True, exclude_defaults=True))
        except Exception as ex:
            self.handle_exception(ex)

    def delete_one(self, item_id):
        item = self.repo.get(item_id)
        self.logger.info(f"Deleting item with id {item}")

        try:
            item = self.repo.delete(item)
        except Exception as ex:
            self.handle_exception(ex)

        return item
