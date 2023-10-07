from datetime import datetime, timedelta, timezone

from pydantic import UUID4

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


def create_mealplan_timeline_events(group_id: UUID4 | None = None):
    # Move it back by 1 minute to ensure that midnight processing logs it to the prev day
    event_time = datetime.now(timezone.utc) - timedelta(minutes=1)

    with session_context() as session:
        repos = get_repositories(session)
        if group_id is None:
            # if not specified, we check all groups
            groups_data = repos.groups.page_all(PaginationQuery(page=1, per_page=-1))
            group_ids = [group.id for group in groups_data.items]

        else:
            group_ids = [group_id]

        for group_id in group_ids:
            event_bus_service = EventBusService(session=session, group_id=group_id)

            timeline_events_to_create: list[RecipeTimelineEventCreate] = []
            recipes_to_update: dict[UUID4, RecipeSummary] = {}
            recipe_id_to_slug_map: dict[UUID4, str] = {}

            mealplans = repos.meals.get_for_day(group_id, -1)
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

                query_end_time = datetime.now() - timedelta()
                query_start_time = query_end_time - timedelta(days=1, minutes=1, seconds=5)
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
                if (
                    not last_made or last_made.date() < event_time.date()
                ) and mealplan.recipe_id not in recipes_to_update:
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
                    event_type=EventTypes.recipe_updated,
                    document_data=EventRecipeData(operation=EventOperation.update, recipe_slug=recipe.slug),
                )
