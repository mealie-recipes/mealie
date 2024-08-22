from collections.abc import Callable

from pydantic import UUID4

from mealie.db.db_setup import session_context
from mealie.repos.all_repositories import get_repositories
from mealie.routes.households.controller_shopping_lists import publish_list_item_events
from mealie.schema.response.pagination import OrderDirection, PaginationQuery
from mealie.schema.user.user import DEFAULT_INTEGRATION_ID
from mealie.services.event_bus_service.event_bus_service import EventBusService
from mealie.services.event_bus_service.event_types import EventDocumentDataBase, EventTypes
from mealie.services.household_services.shopping_lists import ShoppingListService

MAX_CHECKED_ITEMS = 100


def _create_publish_event(event_bus_service: EventBusService):
    def publish_event(
        event_type: EventTypes,
        document_data: EventDocumentDataBase,
        group_id: UUID4,
        household_id: UUID4 | None,
        message: str = "",
    ):
        event_bus_service.dispatch(
            integration_id=DEFAULT_INTEGRATION_ID,
            group_id=group_id,
            household_id=household_id,
            event_type=event_type,
            document_data=document_data,
            message=message,
        )

    return publish_event


def _trim_list_items(shopping_list_service: ShoppingListService, shopping_list_id: UUID4, event_publisher: Callable):
    pagination = PaginationQuery(
        page=1,
        per_page=-1,
        query_filter=f'shopping_list_id="{shopping_list_id}" AND checked=true',
        order_by="updated_at",
        order_direction=OrderDirection.desc,
    )
    query = shopping_list_service.list_items.page_all(pagination)
    if len(query.items) <= MAX_CHECKED_ITEMS:
        return

    items_to_delete = query.items[MAX_CHECKED_ITEMS:]
    items_response = shopping_list_service.bulk_delete_items([item.id for item in items_to_delete])
    publish_list_item_events(event_publisher, items_response)


def delete_old_checked_list_items():
    with session_context() as session:
        repos = get_repositories(session)
        groups = repos.groups.page_all(PaginationQuery(page=1, per_page=-1)).items

        for group in groups:
            group_repos = get_repositories(session, group_id=group.id)
            households = group_repos.households.page_all(PaginationQuery(page=1, per_page=-1)).items
            event_bus_service = EventBusService(session=session)
            event_publisher = _create_publish_event(event_bus_service)

            for household in households:
                household_repos = get_repositories(session, group_id=group.id, household_id=household.id)

                shopping_list_service = ShoppingListService(household_repos)
                shopping_list_data = household_repos.group_shopping_lists.page_all(PaginationQuery(page=1, per_page=-1))
                for shopping_list in shopping_list_data.items:
                    _trim_list_items(
                        shopping_list_service,
                        shopping_list.id,
                        event_publisher,
                    )
