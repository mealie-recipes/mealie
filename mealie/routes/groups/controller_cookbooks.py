from functools import cached_property

from fastapi import APIRouter, HTTPException
from pydantic import UUID4

from mealie.core.exceptions import mealie_registered_exceptions
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.mixins import CrudMixins
from mealie.schema import mapper
from mealie.schema.cookbook import CreateCookBook, ReadCookBook, RecipeCookBook, SaveCookBook, UpdateCookBook

router = APIRouter(prefix="/groups/cookbooks", tags=["Groups: Cookbooks"])


@controller(router)
class GroupCookbookController(BaseUserController):
    @cached_property
    def repo(self):
        return self.deps.repos.cookbooks.by_group(self.group_id)

    def registered_exceptions(self, ex: type[Exception]) -> str:
        registered = {
            **mealie_registered_exceptions(self.deps.t),
        }
        return registered.get(ex, "An unexpected error occurred.")

    @cached_property
    def mixins(self):
        return CrudMixins[CreateCookBook, ReadCookBook, UpdateCookBook](
            self.repo,
            self.deps.logger,
            self.registered_exceptions,
        )

    @router.get("", response_model=list[ReadCookBook])
    def get_all(self):
        items = self.repo.get_all()
        items.sort(key=lambda x: x.position)
        return items

    @router.post("", response_model=ReadCookBook, status_code=201)
    def create_one(self, data: CreateCookBook):
        data = mapper.cast(data, SaveCookBook, group_id=self.group_id)
        return self.mixins.create_one(data)

    @router.put("", response_model=list[ReadCookBook])
    def update_many(self, data: list[UpdateCookBook]):
        updated = []

        for cookbook in data:
            cb = self.mixins.update_one(cookbook, cookbook.id)
            updated.append(cb)

        return updated

    @router.get("/{item_id}", response_model=RecipeCookBook)
    def get_one(self, item_id: UUID4 | str):
        match_attr = "slug" if isinstance(item_id, str) else "id"
        cookbook = self.repo.get_one(item_id, match_attr)

        if cookbook is None:
            raise HTTPException(status_code=404)

        return cookbook.cast(
            RecipeCookBook,
            recipes=self.repos.recipes.by_group(self.group_id).by_category_and_tags(
                cookbook.categories, cookbook.tags, cookbook.tools
            ),
        )

    @router.put("/{item_id}", response_model=ReadCookBook)
    def update_one(self, item_id: str, data: CreateCookBook):
        return self.mixins.update_one(data, item_id)  # type: ignore

    @router.delete("/{item_id}", response_model=ReadCookBook)
    def delete_one(self, item_id: str):
        return self.mixins.delete_one(item_id)
