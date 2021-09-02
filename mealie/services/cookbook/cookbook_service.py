from __future__ import annotations

from fastapi import HTTPException, status

from mealie.core.root_logger import get_logger
from mealie.schema.cookbook.cookbook import CreateCookBook, ReadCookBook, RecipeCookBook, SaveCookBook, UpdateCookBook
from mealie.services.base_http_service.base_http_service import BaseHttpService
from mealie.services.events import create_group_event

logger = get_logger(module=__name__)


class CookbookService(BaseHttpService[int, ReadCookBook]):
    event_func = create_group_event
    _restrict_by_group = True

    _schema = ReadCookBook
    _create_schema = CreateCookBook
    _update_schema = UpdateCookBook
    _get_one_schema = RecipeCookBook

    def populate_item(self, id: int | str):
        try:
            id = int(id)
        except Exception:
            pass

        if isinstance(id, int):
            self.item = self.db.cookbooks.get_one(self.session, id, override_schema=RecipeCookBook)

        else:
            self.item = self.db.cookbooks.get_one(self.session, id, key="slug", override_schema=RecipeCookBook)

    def get_all(self) -> list[ReadCookBook]:
        items = self.db.cookbooks.get(self.session, self.group_id, "group_id", limit=999)
        items.sort(key=lambda x: x.position)
        return items

    def create_one(self, data: CreateCookBook) -> ReadCookBook:
        try:
            self.item = self.db.cookbooks.create(self.session, SaveCookBook(group_id=self.group_id, **data.dict()))
        except Exception as ex:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail={"message": "PAGE_CREATION_ERROR", "exception": str(ex)}
            )

        return self.item

    def update_one(self, data: CreateCookBook, id: int = None) -> ReadCookBook:
        if not self.item:
            return

        target_id = id or self.item.id
        self.item = self.db.cookbooks.update(self.session, target_id, data)

        return self.item

    def update_many(self, data: list[ReadCookBook]) -> list[ReadCookBook]:
        updated = []

        for cookbook in data:
            cb = self.db.cookbooks.update(self.session, cookbook.id, cookbook)
            updated.append(cb)

        return updated

    def delete_one(self, id: int = None) -> ReadCookBook:
        if not self.item:
            return

        target_id = id or self.item.id
        self.item = self.db.cookbooks.delete(self.session, target_id)

        return self.item
