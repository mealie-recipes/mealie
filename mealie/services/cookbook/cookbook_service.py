from __future__ import annotations

from fastapi import HTTPException, status

from mealie.core.root_logger import get_logger
from mealie.schema.cookbook.cookbook import CreateCookBook, ReadCookBook, RecipeCookBook, SaveCookBook
from mealie.services.base_http_service.base_http_service import BaseHttpService
from mealie.services.events import create_group_event

logger = get_logger(module=__name__)


class CookbookService(BaseHttpService[int, str]):
    """
    Class Methods:
        `read_existing`: Reads an existing recipe from the database.
        `write_existing`: Updates an existing recipe in the database.
        `base`: Requires write permissions, but doesn't perform recipe checks
    """

    event_func = create_group_event
    cookbook: ReadCookBook  # Required for proper type hints

    _group_id_cache = None

    @property
    def group_id(self):
        # TODO: Populate Group in Private User Call WARNING: May require significant refactoring
        if not self._group_id_cache:
            group = self.db.groups.get(self.session, self.user.group, "name")
            print(group)
            self._group_id_cache = group.id
        return self._group_id_cache

    def assert_existing(self, id: str):
        self.populate_cookbook(id)

        if not self.cookbook:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        if self.cookbook.group_id != self.group_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

    def populate_cookbook(self, id: int | str):
        try:
            id = int(id)
        except Exception:
            pass

        if isinstance(id, int):
            self.cookbook = self.db.cookbooks.get_one(self.session, id, override_schema=RecipeCookBook)

        else:
            self.cookbook = self.db.cookbooks.get_one(self.session, id, key="slug", override_schema=RecipeCookBook)

    def get_all(self) -> list[ReadCookBook]:
        items = self.db.cookbooks.get(self.session, self.group_id, "group_id", limit=999)
        items.sort(key=lambda x: x.position)
        return items

    def create_one(self, data: CreateCookBook) -> ReadCookBook:
        try:
            self.cookbook = self.db.cookbooks.create(self.session, SaveCookBook(group_id=self.group_id, **data.dict()))
        except Exception as ex:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail={"message": "PAGE_CREATION_ERROR", "exception": str(ex)}
            )

        return self.cookbook

    def update_one(self, data: CreateCookBook, id: int = None) -> ReadCookBook:
        if not self.cookbook:
            return

        target_id = id or self.cookbook.id
        self.cookbook = self.db.cookbooks.update(self.session, target_id, data)

        return self.cookbook

    def update_many(self, data: list[ReadCookBook]) -> list[ReadCookBook]:
        updated = []

        for cookbook in data:
            cb = self.db.cookbooks.update(self.session, cookbook.id, cookbook)
            updated.append(cb)

        return updated

    def delete_one(self, id: int = None) -> ReadCookBook:
        if not self.cookbook:
            return

        target_id = id or self.cookbook.id
        self.cookbook = self.db.cookbooks.delete(self.session, target_id)

        return self.cookbook
