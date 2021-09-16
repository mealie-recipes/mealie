from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from mealie.core.root_logger import get_logger
from mealie.db.data_access_layer.db_access import DatabaseAccessLayer

C = TypeVar("C", bound=BaseModel)
R = TypeVar("R", bound=BaseModel)
U = TypeVar("U", bound=BaseModel)
DAL = TypeVar("DAL", bound=DatabaseAccessLayer)
logger = get_logger()


class CrudHttpMixins(Generic[C, R, U], ABC):
    item: C
    session: Session

    @property
    @abstractmethod
    def dal(self) -> DAL:
        ...

    def populate_item(self, id: int) -> R:
        self.item = self.dal.get_one(id)
        print(self.item)
        return self.item

    def _create_one(self, data: C, exception_msg="generic-create-error") -> R:
        try:
            self.item = self.dal.create(data)
        except Exception as ex:
            logger.exception(ex)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail={"message": exception_msg, "exception": str(ex)})

        return self.item

    def _update_one(self, data: U, item_id: int = None) -> R:
        if not self.item:
            return

        target_id = item_id or self.item.id
        self.item = self.dal.update(target_id, data)

        return self.item

    def _patch_one(self) -> None:
        raise NotImplementedError

    def _delete_one(self, item_id: int = None) -> None:
        if not self.item:
            return

        target_id = item_id or self.item.id
        self.item = self.dal.delete(target_id)
        return self.item
