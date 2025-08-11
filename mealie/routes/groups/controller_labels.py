from functools import cached_property

from fastapi import APIRouter, Depends
from pydantic import UUID4

from mealie.routes._base.base_controllers import BaseCrudController
from mealie.routes._base.controller import controller
from mealie.routes._base.mixins import HttpRepo
from mealie.routes._base.routers import MealieCrudRoute
from mealie.schema.labels import (
    MultiPurposeLabelCreate,
    MultiPurposeLabelOut,
    MultiPurposeLabelSummary,
    MultiPurposeLabelUpdate,
)
from mealie.schema.labels.multi_purpose_label import MultiPurposeLabelPagination
from mealie.schema.response.pagination import PaginationQuery
from mealie.services.event_bus_service.event_types import EventLabelData, EventOperation, EventTypes
from mealie.services.group_services.labels_service import MultiPurposeLabelService

router = APIRouter(prefix="/groups/labels", tags=["Groups: Multi Purpose Labels"], route_class=MealieCrudRoute)


@controller(router)
class MultiPurposeLabelsController(BaseCrudController):
    @cached_property
    def service(self):
        return MultiPurposeLabelService(self.repos)

    @cached_property
    def repo(self):
        if not self.user:
            raise Exception("No user is logged in.")

        return self.repos.group_multi_purpose_labels

    # =======================================================================
    # CRUD Operations

    @property
    def mixins(self) -> HttpRepo:
        return HttpRepo(self.repo, self.logger, self.registered_exceptions, self.t("generic.server-error"))

    @router.get("", response_model=MultiPurposeLabelPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery), search: str | None = None):
        response = self.repo.page_all(
            pagination=q,
            override=MultiPurposeLabelSummary,
            search=search,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=MultiPurposeLabelOut)
    def create_one(self, data: MultiPurposeLabelCreate):
        new_label = self.service.create_one(data)
        self.publish_event(
            event_type=EventTypes.label_created,
            document_data=EventLabelData(operation=EventOperation.create, label_id=new_label.id),
            group_id=new_label.group_id,
            household_id=None,
            message=self.t("notifications.generic-created", name=new_label.name),
        )
        return new_label

    @router.get("/{item_id}", response_model=MultiPurposeLabelOut)
    def get_one(self, item_id: UUID4):
        return self.repo.get_one(item_id)

    @router.put("/{item_id}", response_model=MultiPurposeLabelOut)
    def update_one(self, item_id: UUID4, data: MultiPurposeLabelUpdate):
        label = self.mixins.update_one(data, item_id)
        self.publish_event(
            event_type=EventTypes.label_updated,
            document_data=EventLabelData(operation=EventOperation.update, label_id=label.id),
            group_id=label.group_id,
            household_id=None,
            message=self.t("notifications.generic-updated", name=label.name),
        )
        return label

    @router.delete("/{item_id}", response_model=MultiPurposeLabelOut)
    def delete_one(self, item_id: UUID4):
        label = self.mixins.delete_one(item_id)
        if label:
            self.publish_event(
                event_type=EventTypes.label_deleted,
                document_data=EventLabelData(operation=EventOperation.delete, label_id=label.id),
                group_id=label.group_id,
                household_id=None,
                message=self.t("notifications.generic-deleted", name=label.name),
            )
        return label
