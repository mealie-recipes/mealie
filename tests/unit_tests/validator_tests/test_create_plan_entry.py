from datetime import date

import pytest

from mealie.schema.meal_plan.new_meal import CreatePlanEntry


def test_create_plan_with_title():
    entry = CreatePlanEntry(date=date.today(), title="Test Title")

    assert entry.title == "Test Title"
    assert entry.recipe_id is None


def test_create_plan_with_slug():
    entry = CreatePlanEntry(date=date.today(), recipe_id=123)

    assert entry.recipe_id == 123
    assert entry.title == ""


def test_slug_or_title_validation():
    with pytest.raises(ValueError):
        CreatePlanEntry(date=date.today(), slug="", title="")
