import secrets
from collections.abc import Iterable
from datetime import UTC, date, datetime, time, timedelta, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dateutil.tz import tzlocal
from pydantic import field_validator
from sqlalchemy.orm import Session

from mealie.lang.providers import Translator
from mealie.repos.all_repositories import get_repositories
from mealie.schema._mealie import MealieModel
from mealie.schema.meal_plan.mealplan_ical import ReadMealPlanICalToken
from mealie.schema.meal_plan.new_meal import PlanEntryType, ReadPlanEntry
from mealie.schema.response.pagination import OrderDirection, PaginationQuery
from mealie.services._base_service import BaseService
from mealie.services.urls.url_constructors import recipe_url

EVENT_DURATION = timedelta(hours=1)


class MealPlanICalQuery(MealieModel):
    """Query parameters of the public feed; kept out of `mealie.schema` since the frontend never sends it as JSON"""

    types: list[PlanEntryType] | None = None
    """Only include these meal types; all types are included when empty"""
    include_notes: bool = True
    """Include entries that have no recipe attached"""
    tz: str | None = None
    """IANA timezone used for timed events, e.g. `Europe/Berlin`; defaults to the server timezone"""

    # Event start time per meal type; types without a time are published as all-day events
    breakfast: time | None = None
    lunch: time | None = None
    dinner: time | None = None
    side: time | None = None
    snack: time | None = None
    drink: time | None = None
    dessert: time | None = None

    @field_validator("tz")
    @classmethod
    def validate_tz(cls, value: str | None) -> str | None:
        if not value:
            return None
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as e:
            raise ValueError(f"unknown timezone: {value}") from e
        return value

    def time_for(self, entry_type: PlanEntryType) -> time | None:
        return getattr(self, entry_type.value)


def generate_ical_token() -> str:
    return secrets.token_urlsafe(32)


def _escape_text(value: str) -> str:
    """Escapes a TEXT property value (RFC 5545 section 3.3.11)"""
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\r", "\\n")
        .replace("\n", "\\n")
    )


def _fold(line: str) -> str:
    """Folds a content line to at most 75 octets per line (RFC 5545 section 3.1), without splitting characters"""
    parts: list[str] = []
    current = ""
    current_len = 0
    for char in line:
        char_len = len(char.encode("utf-8"))
        # continuation lines start with a space, which counts towards the limit
        limit = 75 if not parts else 74
        if current_len + char_len > limit:
            parts.append(current)
            current, current_len = "", 0
        current += char
        current_len += char_len
    parts.append(current)
    return "\r\n ".join(parts)


def _format_date(value: date) -> str:
    return value.strftime("%Y%m%d")


def _format_utc(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


class MealPlanICalService(BaseService):
    def __init__(self, session: Session, translator: Translator) -> None:
        self.session = session
        self.translator = translator
        super().__init__()

    def get_feed(self, token: str, query: MealPlanICalQuery) -> str | None:
        """Returns the iCal feed for the household that owns `token`, or None if the token is unknown"""
        repos = get_repositories(self.session, group_id=None, household_id=None)
        prefs = repos.household_preferences.get_one(
            token, key="mealplan_ical_token", override_schema=ReadMealPlanICalToken
        )
        if not prefs or not prefs.mealplan_ical_token:
            return None

        household = repos.households.get_one(prefs.household_id)
        if not household:
            return None
        group = repos.groups.get_one(household.group_id)
        if not group:
            return None

        household_repos = get_repositories(self.session, group_id=group.id, household_id=household.id)
        pagination = PaginationQuery(page=1, per_page=-1, order_by="date", order_direction=OrderDirection.asc)
        entries = household_repos.meals.page_all(pagination).items
        entries = [e for e in entries if self._include(e, query)]

        tz: tzinfo = ZoneInfo(query.tz) if query.tz else tzlocal()
        return self.build_calendar(
            entries, query, tz, calendar_name=f"Mealie - {household.name}", group_slug=group.slug
        )

    @staticmethod
    def _include(entry: ReadPlanEntry, query: MealPlanICalQuery) -> bool:
        if query.types and entry.entry_type not in query.types:
            return False
        if not entry.recipe and not query.include_notes:
            return False
        return True

    def build_calendar(
        self,
        entries: Iterable[ReadPlanEntry],
        query: MealPlanICalQuery,
        tz: tzinfo,
        calendar_name: str,
        group_slug: str,
    ) -> str:
        now = datetime.now(UTC)
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Mealie//Meal Plan//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            f"X-WR-CALNAME:{_escape_text(calendar_name)}",
        ]
        for entry in entries:
            lines.extend(self._event_lines(entry, query, tz, group_slug, now))
        lines.append("END:VCALENDAR")
        return "".join(_fold(line) + "\r\n" for line in lines)

    def _event_lines(
        self, entry: ReadPlanEntry, query: MealPlanICalQuery, tz: tzinfo, group_slug: str, now: datetime
    ) -> list[str]:
        entry_type = self.translator.t(f"mealplan.entry-type.{entry.entry_type.value}", default=entry.entry_type.value)
        entry_type = entry_type[:1].upper() + entry_type[1:]
        title = entry.recipe.name if entry.recipe else entry.title
        url = recipe_url(group_slug, entry.recipe.slug, self.settings.BASE_URL) if entry.recipe else None
        description = "\n\n".join(part for part in [entry.text, url] if part)

        lines = [
            "BEGIN:VEVENT",
            f"UID:mealplan-{entry.id}-{entry.group_id}@mealie",
            f"DTSTAMP:{_format_utc(now)}",
        ]

        start_time = query.time_for(entry.entry_type)
        if start_time:
            start = datetime.combine(entry.date, start_time, tzinfo=tz)
            lines.append(f"DTSTART:{_format_utc(start)}")
            lines.append(f"DTEND:{_format_utc(start + EVENT_DURATION)}")
        else:
            lines.append(f"DTSTART;VALUE=DATE:{_format_date(entry.date)}")
            lines.append(f"DTEND;VALUE=DATE:{_format_date(entry.date + timedelta(days=1))}")

        lines.append(f"SUMMARY:{_escape_text(f'{entry_type}: {title}')}")
        if description:
            lines.append(f"DESCRIPTION:{_escape_text(description)}")
        if url:
            lines.append(f"URL:{url}")
        lines.append("TRANSP:TRANSPARENT")
        lines.append("END:VEVENT")
        return lines
