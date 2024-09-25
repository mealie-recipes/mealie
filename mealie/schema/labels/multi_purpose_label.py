from __future__ import annotations

from typing import ClassVar

from pydantic import UUID4, ConfigDict

from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import PaginationBase


class MultiPurposeLabelCreate(MealieModel):
    name: str
    color: str = "#959595"


class MultiPurposeLabelSave(MultiPurposeLabelCreate):
    group_id: UUID4


class MultiPurposeLabelUpdate(MultiPurposeLabelSave):
    id: UUID4


class MultiPurposeLabelSummary(MultiPurposeLabelUpdate):
    _searchable_properties: ClassVar[list[str]] = ["name"]
    model_config = ConfigDict(from_attributes=True)


class MultiPurposeLabelPagination(PaginationBase):
    items: list[MultiPurposeLabelSummary]


class MultiPurposeLabelOut(MultiPurposeLabelUpdate):
    model_config = ConfigDict(from_attributes=True)
