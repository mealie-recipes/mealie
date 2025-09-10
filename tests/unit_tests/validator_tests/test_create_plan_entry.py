from datetime import UTC, datetime
from uuid import uuid4

import pytest

from mealie.schema.meal_plan.new_meal import CreatePlanEntry


def test_create_plan_with_title():
    entry = CreatePlanEntry(date=datetime.now(UTC).date(), title="Test Title")

    assert entry.title == "Test Title"
    assert entry.recipe_id is None


def test_create_plan_with_slug():
    uuid = uuid4()
    entry = CreatePlanEntry(date=datetime.now(UTC).date(), recipe_id=uuid)

    assert entry.recipe_id == uuid
    assert entry.title == ""


def test_slug_or_title_validation():
    with pytest.raises(ValueError):
        CreatePlanEntry(date=datetime.now(UTC).date(), slug="", title="")
