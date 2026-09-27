"""add structured recipe times

Revision ID: 27621d27c7e1
Revises: 3527efeeec34
Create Date: 2026-09-24 13:16:56.000000

Recipe times were free text. This adds a structured duration (in seconds) next to each one and
moves existing text into it, but only when the whole string is unambiguously a duration: an ISO
8601 duration, a bare number of minutes (what the scraper treated numbers as), or amounts with
unit words from any locale's `datetime` translations (what the scraper wrote via
`pretty_print_timedelta`). Anything else is left as text, untouched.

The one exception is "none", which the scraper wrote for a zero-length time. It's cleared.

The parser lives here rather than in the app so later changes to the scraper can't change what
this migration did.

"""

import json
import re
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

import isodate
import sqlalchemy as sa
from sqlalchemy import orm, text

from alembic import op
from mealie.core.root_logger import get_logger

# revision identifiers, used by Alembic.
revision = "27621d27c7e1"
down_revision: str | None = "3527efeeec34"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None

LOCALES_DIR = Path(__file__).parents[2] / "lang" / "messages"

MAX_SECONDS = 2**31 - 1
"""Postgres INTEGER max"""

TIME_FIELDS = ("total_time", "prep_time", "perform_time")

UNIT_SECONDS = {"day": 86400, "hour": 3600, "minute": 60, "second": 1}
"""Largest first; components must appear in this order, each at most once"""

NUMBER = r"\d+(?:\.\d+)?"

EMPTY_TIME = "none"


def load_unit_words(locales_dir: Path = LOCALES_DIR) -> dict[str, str]:
    """Maps every casefolded singular/plural unit word in every locale to its unit.

    A word that means different units in different locales can't be read safely, so it's dropped.
    """
    words: dict[str, str] = {}
    ambiguous: set[str] = set()

    for path in locales_dir.glob("*.json"):
        try:
            translations = json.loads(path.read_text(encoding="utf-8")).get("datetime") or {}
        except OSError, ValueError, AttributeError:
            continue

        for unit in UNIT_SECONDS:
            for word in str(translations.get(unit) or "").split("|"):
                if not (word := word.strip().casefold()):
                    continue
                if words.setdefault(word, unit) != unit:
                    ambiguous.add(word)

    for word in ambiguous:
        del words[word]

    return words


def build_component_pattern(unit_words: dict[str, str]) -> re.Pattern[str]:
    # Longest first so "minutes" is tried before "minute"
    alternatives = "|".join(re.escape(w) for w in sorted(unit_words, key=len, reverse=True))
    return re.compile(rf"\s*({NUMBER})\s*({alternatives})(?=\s|\d|$)")


def _to_seconds(amount: Decimal) -> int | None:
    if amount <= 0 or amount != amount.to_integral_value() or amount > MAX_SECONDS:
        return None
    return int(amount)


def _parse_iso(value: str) -> int | None:
    try:
        delta = isodate.parse_duration(value)
    except isodate.ISO8601Error, ValueError:
        return None

    # Years and months parse to an isodate.Duration, which has no fixed length
    if not isinstance(delta, timedelta):
        return None

    return _to_seconds(Decimal(str(delta.total_seconds())))


def _parse_words(value: str, unit_words: dict[str, str], pattern: re.Pattern[str]) -> int | None:
    value = value.casefold()
    total = Decimal(0)
    seen_units: list[str] = []
    pos = 0

    while pos < len(value):
        if not (m := pattern.match(value, pos)):
            return None

        unit = unit_words[m.group(2)]
        order = list(UNIT_SECONDS)
        if seen_units and order.index(unit) <= order.index(seen_units[-1]):
            return None

        seen_units.append(unit)
        total += Decimal(m.group(1)) * UNIT_SECONDS[unit]
        pos = m.end()
        if not value[pos:].strip():
            break

    if not seen_units:
        return None

    return _to_seconds(total)


def parse_seconds(value: str | None, unit_words: dict[str, str], pattern: re.Pattern[str]) -> int | None:
    """The duration in seconds, or None if `value` isn't entirely and unambiguously a duration."""
    if not value or not (value := value.strip()):
        return None

    if re.fullmatch(NUMBER, value):
        try:
            return _to_seconds(Decimal(value) * 60)
        except InvalidOperation:
            return None

    if value[0] in "Pp":
        return _parse_iso(value.upper())

    return _parse_words(value, unit_words, pattern)


def is_empty_time(value: str | None) -> bool:
    """What `pretty_print_timedelta` wrote, untranslated, for a zero-length time"""
    return value is not None and value.strip().casefold() == EMPTY_TIME


def format_seconds(seconds: int) -> str:
    """English text for downgrading, in the shape the scraper used to write"""
    parts: list[str] = []
    for unit, size in UNIT_SECONDS.items():
        n, seconds = divmod(seconds, size)
        if n:
            parts.append(f"{n} {unit}{'' if n == 1 else 's'}")
    return " ".join(parts)


def upgrade() -> None:
    with op.batch_alter_table("recipes", schema=None) as batch_op:
        for field in TIME_FIELDS:
            batch_op.add_column(sa.Column(f"{field}_seconds", sa.Integer(), nullable=True))

    logger = get_logger()
    unit_words = load_unit_words()
    pattern = build_component_pattern(unit_words)
    session = orm.Session(bind=op.get_bind())

    rows = session.execute(text(f"SELECT id, {', '.join(TIME_FIELDS)} FROM recipes")).fetchall()
    converted = cleared = 0
    for recipe_id, *values in rows:
        updates: dict[str, int | None] = {}
        for field, value in zip(TIME_FIELDS, values, strict=True):
            if (seconds := parse_seconds(value, unit_words, pattern)) is not None:
                updates[field] = seconds
                converted += 1
            elif is_empty_time(value):
                updates[field] = None
                cleared += 1

        if not updates:
            continue

        assignments = ", ".join(f"{field}_seconds = :{field}, {field} = NULL" for field in updates)
        session.execute(text(f"UPDATE recipes SET {assignments} WHERE id = :id"), {**updates, "id": recipe_id})

    session.commit()
    logger.info(
        "Converted %s recipe times to structured durations and cleared %s empty ones across %s recipes",
        converted,
        cleared,
        len(rows),
    )


def downgrade():
    # Put the text back for times the upgrade moved out, so nothing is lost
    session = orm.Session(bind=op.get_bind())
    for field in TIME_FIELDS:
        rows = session.execute(
            text(f"SELECT id, {field}_seconds FROM recipes WHERE {field} IS NULL AND {field}_seconds IS NOT NULL")
        ).fetchall()
        for recipe_id, seconds in rows:
            session.execute(
                text(f"UPDATE recipes SET {field} = :value WHERE id = :id"),
                {"value": format_seconds(seconds), "id": recipe_id},
            )
    session.commit()

    with op.batch_alter_table("recipes", schema=None) as batch_op:
        for field in reversed(TIME_FIELDS):
            batch_op.drop_column(f"{field}_seconds")
