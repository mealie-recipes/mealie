import re
from collections.abc import Iterable
from datetime import UTC, date, datetime, time, timedelta, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dateutil.tz import tzlocal
from pydantic import Field, field_validator
from sqlalchemy.orm import Session

from mealie.lang.providers import Translator
from mealie.repos.all_repositories import get_repositories
from mealie.schema._mealie import MealieModel
from mealie.schema.meal_plan.mealplan_ical import ReadMealPlanICalToken
from mealie.schema.meal_plan.new_meal import PlanEntryType, ReadPlanEntry
from mealie.schema.response.pagination import OrderDirection, PaginationQuery
from mealie.services._base_service import BaseService
from mealie.services.urls.url_constructors import recipe_url

EVENT_DURATION_MINUTES = 60
REFRESH_INTERVAL = "PT1H"
"""How often calendar apps should poll the feed (ISO 8601 duration); only a hint, some apps (e.g. Google) ignore it"""
FEED_HISTORY_DAYS = 90
"""How many days of past entries the feed includes; future entries are always included"""
SUMMARY_TEMPLATE = "${type}: ${title}"
DESCRIPTION_TEMPLATE = "${text}\n\n${url}"
TEMPLATE_MAX_LENGTH = 500
MERGE_FIELD = re.compile(r"\$\{(\w+)\}")


class MealPlanICalQuery(MealieModel):
    """Query parameters of the public feed; kept out of `mealie.schema` since the frontend never sends it as JSON"""

    types: list[PlanEntryType] | None = None
    """Only include these meal types; all types are included when empty"""
    include_notes: bool = True
    """Include entries that have no recipe attached"""
    tz: str | None = None
    """IANA timezone used for timed events, e.g. `Europe/Berlin`; defaults to the server timezone"""
    lang: str | None = None
    """Locale of translated text, e.g. `de-DE`; needed since calendar apps don't send the user's language"""
    duration: int = Field(EVENT_DURATION_MINUTES, ge=1, le=24 * 60)
    """Length of timed events, in minutes"""
    summary: str = Field(SUMMARY_TEMPLATE, max_length=TEMPLATE_MAX_LENGTH)
    """Event title; `${field}` merge fields are replaced with the entry's values"""
    description: str = Field(DESCRIPTION_TEMPLATE, max_length=TEMPLATE_MAX_LENGTH)
    """Event description; `${field}` merge fields are replaced with the entry's values"""

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


def _render_template(template: str, fields: dict[str, str]) -> str:
    """Replaces `${field}` merge fields (same syntax as recipe actions) with their values; missing fields are empty"""
    rendered = MERGE_FIELD.sub(lambda match: fields.get(match.group(1), ""), template)
    # empty fields would otherwise leave stray blank lines behind
    return re.sub(r"\n{3,}", "\n\n", rendered).strip()


def _format_number(value: float) -> str:
    return f"{value:g}"


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
        # past entries would otherwise grow forever and be re-sent on every calendar poll
        since = datetime.now(UTC).date() - timedelta(days=FEED_HISTORY_DAYS)
        pagination = PaginationQuery(
            page=1,
            per_page=-1,
            order_by="date",
            order_direction=OrderDirection.asc,
            query_filter=f"date >= {since}",
        )
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
            f"NAME:{_escape_text(calendar_name)}",
            f"X-WR-CALNAME:{_escape_text(calendar_name)}",
            f"REFRESH-INTERVAL;VALUE=DURATION:{REFRESH_INTERVAL}",
            f"X-PUBLISHED-TTL:{REFRESH_INTERVAL}",
        ]
        if query.tz:
            lines.append(f"X-WR-TIMEZONE:{query.tz}")
        for entry in entries:
            lines.extend(self._event_lines(entry, query, tz, group_slug, now))
        lines.append("END:VCALENDAR")
        return "".join(_fold(line) + "\r\n" for line in lines)

    def _merge_fields(self, entry: ReadPlanEntry, url: str | None) -> dict[str, str]:
        # when adding or removing fields, also update the "Calendar Feed" list in docs/.../getting-started/features.md
        entry_type = self.translator.t(f"mealplan.entry-type.{entry.entry_type.value}", default=entry.entry_type.value)
        fields = {
            "type": entry_type[:1].upper() + entry_type[1:],
            "title": entry.title,
            "text": entry.text,
            "url": url or "",
        }

        recipe = entry.recipe
        if not recipe:
            return fields

        # servings and yield match recipe actions, which treat a missing value as 1
        fields.update(
            {
                "title": recipe.name or "",
                "id": str(recipe.id) if recipe.id else "",
                "slug": recipe.slug,
                "servings": _format_number((recipe.recipe_servings or 1) * entry.recipe_scale),
                "yieldQuantity": _format_number((recipe.recipe_yield_quantity or 1) * entry.recipe_scale),
                "yieldText": recipe.recipe_yield or "",
                "description": recipe.description or "",
                "totalTime": recipe.total_time or "",
                "prepTime": recipe.prep_time or "",
                "cookTime": recipe.cook_time or "",
                "tags": ", ".join(tag.name for tag in recipe.tags or []),
                "categories": ", ".join(category.name for category in recipe.recipe_category or []),
                "tools": ", ".join(tool.name for tool in recipe.tools),
            }
        )
        return fields

    def _event_lines(
        self, entry: ReadPlanEntry, query: MealPlanICalQuery, tz: tzinfo, group_slug: str, now: datetime
    ) -> list[str]:
        url = recipe_url(group_slug, entry.recipe.slug, self.settings.BASE_URL) if entry.recipe else None
        fields = self._merge_fields(entry, url)
        summary = _render_template(query.summary, fields)
        description = _render_template(query.description, fields)

        lines = [
            "BEGIN:VEVENT",
            f"UID:mealplan-{entry.id}-{entry.group_id}@mealie",
            f"DTSTAMP:{_format_utc(now)}",
        ]

        # date range entries (e.g. a week) aren't on a specific day, so they're always all-day events spanning the range
        start_time = None if entry.end_date else query.time_for(entry.entry_type)
        if start_time:
            start = datetime.combine(entry.date, start_time, tzinfo=tz)
            lines.append(f"DTSTART:{_format_utc(start)}")
            lines.append(f"DTEND:{_format_utc(start + timedelta(minutes=query.duration))}")
        else:
            # DTEND is exclusive, so it's the day after the last day
            last_day = entry.end_date or entry.date
            lines.append(f"DTSTART;VALUE=DATE:{_format_date(entry.date)}")
            lines.append(f"DTEND;VALUE=DATE:{_format_date(last_day + timedelta(days=1))}")

        lines.append(f"SUMMARY:{_escape_text(summary)}")
        categories = [fields["type"]]
        if entry.recipe:
            categories.extend(category.name for category in entry.recipe.recipe_category or [])
        lines.append(f"CATEGORIES:{','.join(_escape_text(category) for category in categories)}")
        if description:
            lines.append(f"DESCRIPTION:{_escape_text(description)}")
        if url:
            lines.append(f"URL:{url}")
        lines.append("TRANSP:TRANSPARENT")
        lines.append("END:VEVENT")
        return lines
