from pydantic import UUID4

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group.group_shopping_list import ShoppingListMultiPurposeLabelCreate
from mealie.schema.labels.multi_purpose_label import (
    MultiPurposeLabelCreate,
    MultiPurposeLabelOut,
    MultiPurposeLabelSave,
)
from mealie.schema.response.pagination import PaginationQuery


class MultiPurposeLabelService:
    def __init__(self, repos: AllRepositories, group_id: UUID4):
        self.repos = repos
        self.group_id = group_id
        self.labels = repos.group_multi_purpose_labels

    def _update_shopping_list_label_references(self, new_labels: list[MultiPurposeLabelOut]) -> None:
        shopping_lists_repo = self.repos.group_shopping_lists.by_group(self.group_id)
        shopping_list_multi_purpose_labels_repo = self.repos.shopping_list_multi_purpose_labels

        shopping_lists = shopping_lists_repo.page_all(PaginationQuery(page=1, per_page=-1))
        new_shopping_list_labels: list[ShoppingListMultiPurposeLabelCreate] = []
        for label in new_labels:
            new_shopping_list_labels.extend(
                [
                    ShoppingListMultiPurposeLabelCreate(
                        shopping_list_id=shopping_list.id, label_id=label.id, position=len(shopping_list.label_settings)
                    )
                    for shopping_list in shopping_lists.items
                ]
            )

        shopping_list_multi_purpose_labels_repo.create_many(new_shopping_list_labels)

    def create_one(self, data: MultiPurposeLabelCreate) -> MultiPurposeLabelOut:
        label = self.labels.create(data.cast(MultiPurposeLabelSave, group_id=self.group_id))
        self._update_shopping_list_label_references([label])
        return label

    def create_many(self, data: list[MultiPurposeLabelCreate]) -> list[MultiPurposeLabelOut]:
        labels = self.labels.create_many([label.cast(MultiPurposeLabelSave, group_id=self.group_id) for label in data])
        self._update_shopping_list_label_references(labels)
        return labels
