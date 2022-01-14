from functools import cached_property

from fastapi import APIRouter, Depends
from pydantic import UUID4

from mealie.routes._base.controller import controller
from mealie.routes._base.dependencies import SharedDependencies
from mealie.routes._base.mixins import CrudMixins
from mealie.schema.group.group_events import (
    GroupEventNotifierCreate,
    GroupEventNotifierOut,
    GroupEventNotifierPrivate,
    GroupEventNotifierSave,
    GroupEventNotifierUpdate,
)
from mealie.schema.mapper import cast
from mealie.schema.query import GetAll
from mealie.services.event_bus_service.event_bus_service import EventBusService

router = APIRouter(prefix="/groups/events/notifications", tags=["Group: Event Notifications"])


@controller(router)
class GroupEventsNotifierController:
    deps: SharedDependencies = Depends(SharedDependencies.user)
    event_bus: EventBusService = Depends(EventBusService)

    @cached_property
    def repo(self):
        if not self.deps.acting_user:
            raise Exception("No user is logged in.")

        return self.deps.repos.group_event_notifier.by_group(self.deps.acting_user.group_id)

    # =======================================================================
    # CRUD Operations

    @property
    def mixins(self) -> CrudMixins:
        return CrudMixins(self.repo, self.deps.logger, self.registered_exceptions, "An unexpected error occurred.")

    @router.get("", response_model=list[GroupEventNotifierOut])
    def get_all(self, q: GetAll = Depends(GetAll)):
        return self.repo.get_all(start=q.start, limit=q.limit)

    @router.post("", response_model=GroupEventNotifierOut, status_code=201)
    def create_one(self, data: GroupEventNotifierCreate):
        save_data = cast(data, GroupEventNotifierSave, group_id=self.deps.acting_user.group_id)
        return self.mixins.create_one(save_data)

    @router.get("/{item_id}", response_model=GroupEventNotifierOut)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=GroupEventNotifierOut)
    def update_one(self, item_id: UUID4, data: GroupEventNotifierUpdate):
        if data.apprise_url is None:
            current_data: GroupEventNotifierPrivate = self.repo.get_one(
                item_id, override_schema=GroupEventNotifierPrivate
            )
            data.apprise_url = current_data.apprise_url

        return self.mixins.update_one(data, item_id)

    @router.delete("/{item_id}", status_code=204)
    def delete_one(self, item_id: UUID4):
        self.mixins.delete_one(item_id)  # type: ignore

    # =======================================================================
    # Test Event Notifications

    @router.post("/{item_id}/test", status_code=204)
    def test_notification(self, item_id: UUID4):
        item: GroupEventNotifierPrivate = self.repo.get_one(item_id, override_schema=GroupEventNotifierPrivate)
        self.event_bus.test_publisher(item.apprise_url)
