from __future__ import annotations

from functools import cached_property

from mealie.core.root_logger import get_logger
from mealie.schema.cookbook.cookbook import CreateCookBook, ReadCookBook, RecipeCookBook, SaveCookBook, UpdateCookBook
from mealie.services._base_http_service.crud_http_mixins import CrudHttpMixins
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_group_event
from mealie.utils.error_messages import ErrorMessages

logger = get_logger(module=__name__)


class CookbookService(
    CrudHttpMixins[CreateCookBook, ReadCookBook, UpdateCookBook],
    UserHttpService[int, ReadCookBook],
):
    event_func = create_group_event
    _restrict_by_group = True
    _schema = ReadCookBook

    @cached_property
    def dal(self):
        return self.new_db.cookbooks

    def populate_item(self, item_id: int) -> RecipeCookBook:
        try:
            item_id = int(item_id)
        except Exception:
            pass

        if isinstance(item_id, int):
            self.item = self.dal.get_one(item_id, override_schema=RecipeCookBook)

        else:
            self.item = self.dal.get_one(item_id, key="slug", override_schema=RecipeCookBook)

    def get_all(self) -> list[ReadCookBook]:
        items = self.dal.get(self.group_id, "group_id", limit=999)
        items.sort(key=lambda x: x.position)
        return items

    def create_one(self, data: CreateCookBook) -> ReadCookBook:
        data = self.cast(data, SaveCookBook)
        return self._create_one(data, ErrorMessages.cookbook_create_failure)

    def update_one(self, data: UpdateCookBook, id: int = None) -> ReadCookBook:
        return self._update_one(data, id)

    def update_many(self, data: list[UpdateCookBook]) -> list[ReadCookBook]:
        updated = []

        for cookbook in data:
            cb = self.dal.update(cookbook.id, cookbook)
            updated.append(cb)

        return updated

    def delete_one(self, id: int = None) -> ReadCookBook:
        return self._delete_one(id)
