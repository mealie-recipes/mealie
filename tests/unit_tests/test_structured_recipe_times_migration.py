import json
from pathlib import Path

import pytest

from tests.utils.alembic_reader import ALEMBIC_MIGRATIONS, import_file


def _migration():
    path = next(ALEMBIC_MIGRATIONS.glob("*27621d27c7e1*.py"))
    return import_file("add_structured_recipe_times", path)


migration = _migration()
UNIT_WORDS = migration.load_unit_words()
PATTERN = migration.build_component_pattern(UNIT_WORDS)


@pytest.mark.parametrize(
    "value, expected",
    [
        # ISO 8601
        ("PT15M", 900),
        ("PT1H30M", 5400),
        ("pt1h", 3600),
        ("P1DT2H", 93600),
        ("PT90S", 90),
        # Bare numbers were treated as minutes by the scraper
        ("30", 1800),
        ("1.5", 90),
        # What pretty_print_timedelta wrote, in any locale
        ("1 hour 30 minutes", 5400),
        ("1 Hour", 3600),
        ("2 days 4 hours", 187200),
        ("45 seconds", 45),
        ("1 Stunde 30 Minuten", 5400),
        ("2 heures 15 minutes", 8100),
        ("1 時間 30 分", 5400),
        ("1時間30分", 5400),
        ("1.5 hours", 5400),
        ("  20 minutes  ", 1200),
    ],
)
def test_parse_seconds(value: str, expected: int) -> None:
    assert migration.parse_seconds(value, UNIT_WORDS, PATTERN) == expected


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "   ",
        # Not entirely a duration
        "about 30 minutes",
        "30 minutes, plus overnight",
        "1 hour and 30 minutes",
        "1 hour, 30 minutes",
        "Overnight",
        "none",
        # Units out of order or repeated
        "30 minutes 1 hour",
        "10 minutes 5 minutes",
        # Unknown words or abbreviations
        "30 mins",
        "1 hr",
        # Nothing to store
        "0",
        "PT0M",
        "0 minutes",
        # Not whole seconds
        "PT0.5S",
        "0.001",
        # No fixed length
        "P1M",
        "P1Y",
        # Too large for a Postgres INTEGER
        "P30000D",
        # Not a valid ISO duration
        "PTXM",
    ],
)
def test_parse_seconds_leaves_text_alone(value: str | None) -> None:
    assert migration.parse_seconds(value, UNIT_WORDS, PATTERN) is None


def test_ambiguous_unit_words_are_dropped(tmp_path: Path) -> None:
    tmp_path.joinpath("aa-AA.json").write_text(json.dumps({"datetime": {"hour": "tick|ticks", "minute": "min"}}))
    tmp_path.joinpath("bb-BB.json").write_text(json.dumps({"datetime": {"second": "tick|tock"}}))
    tmp_path.joinpath("broken.json").write_text("{")

    assert migration.load_unit_words(tmp_path) == {"ticks": "hour", "min": "minute", "tock": "second"}


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (60, "1 minute"),
        (5400, "1 hour 30 minutes"),
        (93690, "1 day 2 hours 1 minute 30 seconds"),
    ],
)
def test_format_seconds(seconds: int, expected: str) -> None:
    assert migration.format_seconds(seconds) == expected
