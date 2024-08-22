from mealie.repos.all_repositories import get_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.household.group_shopping_list import ShoppingListMultiPurposeLabelCreate
from mealie.schema.labels.multi_purpose_label import (
    MultiPurposeLabelCreate,
    MultiPurposeLabelOut,
    MultiPurposeLabelSave,
)
from mealie.schema.response.pagination import PaginationQuery


class MultiPurposeLabelService:
    def __init__(self, repos: AllRepositories):
        self.repos = repos
        self.labels = repos.group_multi_purpose_labels

    def _update_shopping_list_label_references(self, new_labels: list[MultiPurposeLabelOut]) -> None:
        # remove the households filter so we get all lists
        household_repos = get_repositories(self.repos.session, group_id=self.repos.group_id, household_id=None)
        shopping_lists_repo = household_repos.group_shopping_lists
        shopping_list_multi_purpose_labels_repo = household_repos.shopping_list_multi_purpose_labels

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
        label = self.labels.create(data.cast(MultiPurposeLabelSave, group_id=self.repos.group_id))
        self._update_shopping_list_label_references([label])
        return label

    def create_many(self, data: list[MultiPurposeLabelCreate]) -> list[MultiPurposeLabelOut]:
        labels = self.labels.create_many(
            [label.cast(MultiPurposeLabelSave, group_id=self.repos.group_id) for label in data]
        )
        self._update_shopping_list_label_references(labels)
        return labels
