from functools import cached_property

from fastapi import APIRouter, Depends
from pydantic import UUID4

from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.routers import MealieCrudRoute
from mealie.schema.group.group_events import (
    GroupEventNotifierCreate,
    GroupEventNotifierOut,
    GroupEventNotifierPrivate,
    GroupEventNotifierSave,
    GroupEventNotifierUpdate,
    GroupEventPagination,
)
from mealie.schema.mapper import cast
from mealie.schema.response.pagination import PaginationQuery
from mealie.services.event_bus_service.event_bus_listeners import AppriseEventListener
from mealie.services.event_bus_service.event_bus_service import EventBusService
from mealie.services.event_bus_service.event_types import (
    Event,
    EventBusMessage,
    EventDocumentDataBase,
    EventDocumentType,
    EventOperation,
    EventTypes,
)

router = APIRouter(
    prefix="/groups/events/notifications", tags=["Group: Event Notifications"], route_class=MealieCrudRoute
)


@controller(router)
class GroupEventsNotifierController(BaseUserController):
    event_bus: EventBusService = Depends(EventBusService.create)

    @cached_property
    def repo(self):
        if not self.user:
            raise Exception("No user is logged in.")

        return self.repos.group_event_notifier.by_group(self.user.group_id)

    # =======================================================================
    # CRUD Operations

    @property
    def mixins(self) -> HttpRepo:
        return HttpRepo(self.repo, self.logger, self.registered_exceptions, "An unexpected error occurred.")

    @router.get("", response_model=GroupEventPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repo.page_all(
            pagination=q,
            override=GroupEventNotifierOut,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.dict())
        return response

    @router.post("", response_model=GroupEventNotifierOut, status_code=201)
    def create_one(self, data: GroupEventNotifierCreate):
        save_data = cast(data, GroupEventNotifierSave, group_id=self.user.group_id)
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

    #  TODO: properly re-implement this with new event listeners
    @router.post("/{item_id}/test", status_code=204)
    def test_notification(self, item_id: UUID4):
        item: GroupEventNotifierPrivate = self.repo.get_one(item_id, override_schema=GroupEventNotifierPrivate)

        event_type = EventTypes.test_message
        test_event = Event(
            message=EventBusMessage.from_type(event_type, "test message"),
            event_type=event_type,
            integration_id="test_event",
            document_data=EventDocumentDataBase(document_type=EventDocumentType.generic, operation=EventOperation.info),
        )

        test_listener = AppriseEventListener(self.event_bus.session, self.group_id)
        test_listener.publish_to_subscribers(test_event, [item.apprise_url])
