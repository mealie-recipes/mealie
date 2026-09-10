from datetime import UTC, datetime
from uuid import uuid4

from freezegun import freeze_time

from mealie.schema.recipe.recipe_timeline_events import RecipeTimelineEventIn, TimelineEventType


@freeze_time("2020-01-01 12:00:00")
def test_omitted_timestamp_is_stamped_at_instance_creation():
    """An omitted timestamp is stamped when the event is created, not at import time.

    A bare ``datetime.now(UTC)`` default is evaluated once when the class is
    defined, so every timestamp-less event in a process run shares the same
    stale value. A ``default_factory`` recomputes it for each instance.
    """
    event = RecipeTimelineEventIn(
        recipe_id=uuid4(),
        subject="made this",
        event_type=TimelineEventType.info,
    )

    assert event.timestamp == datetime(2020, 1, 1, 12, 0, tzinfo=UTC)


def test_explicit_timestamp_is_respected():
    """A supplied timestamp is used verbatim and the default factory is not consulted."""
    supplied = datetime(2021, 6, 15, 8, 30, tzinfo=UTC)
    event = RecipeTimelineEventIn(
        recipe_id=uuid4(),
        subject="made this",
        event_type=TimelineEventType.info,
        timestamp=supplied,
    )

    assert event.timestamp == supplied
