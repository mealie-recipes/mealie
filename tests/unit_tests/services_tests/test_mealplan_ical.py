from datetime import UTC, date, datetime
from uuid import uuid4

from dateutil.tz import tzlocal

from mealie.schema.meal_plan.new_meal import ReadPlanEntry
from mealie.schema.recipe.recipe import RecipeSummary
from mealie.services.household_services.mealplan_ical_service import (
    MealPlanICalQuery,
    MealPlanICalService,
    _escape_text,
    _fold,
    _render_template,
)


class StubTranslator:
    def t(self, key, default=None, **kwargs) -> str:
        return default or key


def test_escape_text():
    assert _escape_text("a\\b;c,d\r\ne\nf") == "a\\\\b\\;c\\,d\\ne\\nf"


def test_fold_short_line_unchanged():
    assert _fold("SUMMARY:Dinner") == "SUMMARY:Dinner"


def test_fold_long_line():
    line = "DESCRIPTION:" + "x" * 200
    folded = _fold(line)

    parts = folded.split("\r\n")
    assert len(parts) > 1
    assert all(len(part.encode()) <= 75 for part in parts)
    assert all(part.startswith(" ") for part in parts[1:])
    assert folded.replace("\r\n ", "") == line


def test_fold_does_not_split_multibyte_characters():
    line = "SUMMARY:" + "🍝ä" * 40
    folded = _fold(line)

    parts = folded.split("\r\n")
    assert all(len(part.encode()) <= 75 for part in parts)
    assert folded.replace("\r\n ", "") == line


def test_render_template():
    fields = {"type": "Dinner", "title": "Pasta", "note": ""}
    assert _render_template("${type}: ${title} (${title})", fields) == "Dinner: Pasta (Pasta)"
    assert _render_template("${unknown}${title}", fields) == "Pasta"
    assert _render_template("${title}", {"title": "${type}"}) == "${type}"


def test_render_template_collapses_empty_fields():
    assert _render_template("${note}\n\n${url}", {"note": "", "url": "https://example.com"}) == "https://example.com"
    assert _render_template("a\n\n${note}\n\nb", {"note": ""}) == "a\n\nb"


def test_last_modified_uses_latest_of_entry_and_recipe():
    entry_updated = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    recipe_updated = datetime(2026, 1, 2, 12, 0, tzinfo=UTC)
    recipe = RecipeSummary(name="Pasta", slug="pasta", updated_at=recipe_updated)
    entry = ReadPlanEntry(
        id=1,
        date=date(2026, 1, 3),
        entry_type="dinner",
        recipe_id=uuid4(),
        group_id=uuid4(),
        user_id=uuid4(),
        household_id=uuid4(),
        recipe=recipe,
        updated_at=entry_updated,
    )
    service = MealPlanICalService(None, StubTranslator())  # type: ignore[arg-type]

    feed = service.build_calendar([entry], MealPlanICalQuery(), tzlocal(), "Mealie", "group")
    assert "LAST-MODIFIED:20260102T120000Z\r\n" in feed
    assert f"SEQUENCE:{int(recipe_updated.timestamp())}\r\n" in feed

    entry.updated_at = datetime(2026, 1, 4, 12, 0, tzinfo=UTC)
    feed = service.build_calendar([entry], MealPlanICalQuery(), tzlocal(), "Mealie", "group")
    assert "LAST-MODIFIED:20260104T120000Z\r\n" in feed
