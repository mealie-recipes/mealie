from datetime import datetime, timezone
from uuid import uuid4

import pytest

from mealie.schema.meal_plan.new_meal import CreatePlanEntry


def test_create_plan_with_title():
    entry = CreatePlanEntry(date=datetime.now(timezone.utc).date(), title="Test Title")

    assert entry.title == "Test Title"
    assert entry.recipe_id is None


def test_create_plan_with_slug():
    uuid = uuid4()
    entry = CreatePlanEntry(date=datetime.now(timezone.utc).date(), recipe_id=uuid)

    assert entry.recipe_id == uuid
    assert entry.title == ""


def test_slug_or_title_validation():
    with pytest.raises(ValueError):
        CreatePlanEntry(date=datetime.now(timezone.utc).date(), slug="", title="")
