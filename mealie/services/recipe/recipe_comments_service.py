from __future__ import annotations

from functools import cached_property
from uuid import UUID

from fastapi import HTTPException

from mealie.schema.recipe.recipe_comments import (
    RecipeCommentCreate,
    RecipeCommentOut,
    RecipeCommentSave,
    RecipeCommentUpdate,
)
from mealie.services._base_http_service.crud_http_mixins import CrudHttpMixins
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_recipe_event


class RecipeCommentsService(
    CrudHttpMixins[RecipeCommentOut, RecipeCommentCreate, RecipeCommentCreate],
    UserHttpService[UUID, RecipeCommentOut],
):
    event_func = create_recipe_event
    _restrict_by_group = False
    _schema = RecipeCommentOut

    @cached_property
    def dal(self):
        return self.db.comments

    def _check_comment_belongs_to_user(self) -> None:
        if self.item.user_id != self.user.id and not self.user.admin:
            raise HTTPException(detail="Comment does not belong to user")

    def populate_item(self, id: UUID) -> RecipeCommentOut:
        self.item = self.dal.get_one(id)
        return self.item

    def get_all(self) -> list[RecipeCommentOut]:
        return self.dal.get_all()

    def create_one(self, data: RecipeCommentCreate) -> RecipeCommentOut:
        save_data = RecipeCommentSave(text=data.text, user_id=self.user.id, recipe_id=data.recipe_id)
        return self._create_one(save_data)

    def update_one(self, data: RecipeCommentUpdate, item_id: UUID = None) -> RecipeCommentOut:
        self._check_comment_belongs_to_user()
        return self._update_one(data, item_id)

    def delete_one(self, item_id: UUID = None) -> RecipeCommentOut:
        self._check_comment_belongs_to_user()
        return self._delete_one(item_id)
