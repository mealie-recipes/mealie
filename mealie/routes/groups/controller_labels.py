from functools import cached_property

from fastapi import APIRouter, Depends
from pydantic import UUID4

from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.schema.labels import (
    MultiPurposeLabelCreate,
    MultiPurposeLabelOut,
    MultiPurposeLabelSave,
    MultiPurposeLabelSummary,
    MultiPurposeLabelUpdate,
)
from mealie.schema.mapper import cast
from mealie.schema.query import GetAll

router = APIRouter(prefix="/groups/labels", tags=["Group: Multi Purpose Labels"])


@controller(router)
class MultiPurposeLabelsController(BaseUserController):
    @cached_property
    def repo(self):
        if not self.deps.acting_user:
            raise Exception("No user is logged in.")

        return self.deps.repos.group_multi_purpose_labels.by_group(self.deps.acting_user.group_id)

    # =======================================================================
    # CRUD Operations

    @property
    def mixins(self) -> HttpRepo:
        return HttpRepo(self.repo, self.deps.logger, self.registered_exceptions, "An unexpected error occurred.")

    @router.get("", response_model=list[MultiPurposeLabelSummary])
    def get_all(self, q: GetAll = Depends(GetAll)):
        return self.repo.get_all(start=q.start, limit=q.limit, override=MultiPurposeLabelSummary)

    @router.post("", response_model=MultiPurposeLabelOut)
    def create_one(self, data: MultiPurposeLabelCreate):
        save_data = cast(data, MultiPurposeLabelSave, group_id=self.deps.acting_user.group_id)
        return self.mixins.create_one(save_data)

    @router.get("/{item_id}", response_model=MultiPurposeLabelOut)
    def get_one(self, item_id: UUID4):
        return self.repo.get_one(item_id)

    @router.put("/{item_id}", response_model=MultiPurposeLabelOut)
    def update_one(self, item_id: UUID4, data: MultiPurposeLabelUpdate):
        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", response_model=MultiPurposeLabelOut)
    def delete_one(self, item_id: UUID4):
        return self.mixins.delete_one(item_id)  # type: ignore
