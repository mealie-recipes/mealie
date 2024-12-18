from datetime import UTC, datetime, time, timedelta

from dateutil.tz import tzlocal
from pydantic import UUID4
from sqlalchemy.orm import Session

from mealie.db.db_setup import session_context
from mealie.repos.all_repositories import get_repositories
from mealie.schema.meal_plan.new_meal import PlanEntryType
from mealie.schema.recipe.recipe import RecipeSummary
from mealie.schema.recipe.recipe_timeline_events import RecipeTimelineEventCreate, TimelineEventType
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.user.user import DEFAULT_INTEGRATION_ID
from mealie.services.event_bus_service.event_bus_service import EventBusService
from mealie.services.event_bus_service.event_types import (
    EventOperation,
    EventRecipeData,
    EventRecipeTimelineEventData,
    EventTypes,
)


def _create_mealplan_timeline_events_for_household(
    event_time: datetime, session: Session, group_id: UUID4, household_id: UUID4
) -> None:
    repos = get_repositories(session, group_id=group_id, household_id=household_id)
    event_bus_service = EventBusService(session=session)

    timeline_events_to_create: list[RecipeTimelineEventCreate] = []
    recipes_to_update: dict[UUID4, RecipeSummary] = {}
    recipe_id_to_slug_map: dict[UUID4, str] = {}

    local_tz = tzlocal()
    mealplans = repos.meals.get_today(tz=local_tz)
    for mealplan in mealplans:
        if not (mealplan.recipe and mealplan.user_id):
            continue

        user = repos.users.get_one(mealplan.user_id)
        if not user:
            continue

        # TODO: make this translatable
        if mealplan.entry_type == PlanEntryType.side:
            event_subject = f"{user.full_name} made this as a side"

        else:
            event_subject = f"{user.full_name} made this for {mealplan.entry_type.value}"

        query_start_time = datetime.combine(datetime.now(UTC).date(), time.min)
        query_end_time = query_start_time + timedelta(days=1)
        query = PaginationQuery(
            query_filter=(
                f'recipe_id = "{mealplan.recipe_id}" '
                f'AND timestamp >= "{query_start_time.isoformat()}" '
                f'AND timestamp < "{query_end_time.isoformat()}" '
                f'AND subject = "{event_subject}"'
            )
        )

        # if this event already exists, don't create it again
        events = repos.recipe_timeline_events.page_all(pagination=query)
        if events.items:
            continue

        # bump up the last made date
        last_made = mealplan.recipe.last_made
        if (not last_made or last_made.date() < event_time.date()) and mealplan.recipe_id not in recipes_to_update:
            recipes_to_update[mealplan.recipe_id] = mealplan.recipe

        timeline_events_to_create.append(
            RecipeTimelineEventCreate(
                user_id=user.id,
                subject=event_subject,
                event_type=TimelineEventType.info,
                timestamp=event_time,
                recipe_id=mealplan.recipe_id,
            )
        )

        recipe_id_to_slug_map[mealplan.recipe_id] = mealplan.recipe.slug

    if not timeline_events_to_create:
        return

    # TODO: use bulk operations
    for event in timeline_events_to_create:
        new_event = repos.recipe_timeline_events.create(event)
        event_bus_service.dispatch(
            integration_id=DEFAULT_INTEGRATION_ID,
            group_id=group_id,
            household_id=household_id,
            event_type=EventTypes.recipe_updated,
            document_data=EventRecipeTimelineEventData(
                operation=EventOperation.create,
                recipe_slug=recipe_id_to_slug_map[new_event.recipe_id],
                recipe_timeline_event_id=new_event.id,
            ),
        )

    for recipe in recipes_to_update.values():
        repos.recipes.patch(recipe.slug, {"last_made": event_time})
        event_bus_service.dispatch(
            integration_id=DEFAULT_INTEGRATION_ID,
            group_id=group_id,
            household_id=household_id,
            event_type=EventTypes.recipe_updated,
            document_data=EventRecipeData(operation=EventOperation.update, recipe_slug=recipe.slug),
        )


def _create_mealplan_timeline_events_for_group(event_time: datetime, session: Session, group_id: UUID4) -> None:
    repos = get_repositories(session, group_id=group_id)
    households_data = repos.households.page_all(PaginationQuery(page=1, per_page=-1))
    household_ids = [household.id for household in households_data.items]
    for household_id in household_ids:
        _create_mealplan_timeline_events_for_household(event_time, session, group_id, household_id)


def create_mealplan_timeline_events() -> None:
    event_time = datetime.now(UTC)

    with session_context() as session:
        repos = get_repositories(session)
        groups_data = repos.groups.page_all(PaginationQuery(page=1, per_page=-1))
        group_ids = [group.id for group in groups_data.items]

        for group_id in group_ids:
            _create_mealplan_timeline_events_for_group(event_time, session, group_id)
