from datetime import UTC, datetime

from sqlalchemy.types import DateTime, TypeDecorator


def get_utc_now():
    """
    Returns the current time in UTC.
    """
    return datetime.now(UTC)


def get_utc_today():
    """
    Returns the current date in UTC.
    """
    return datetime.now(UTC).date()


class NaiveDateTime(TypeDecorator):
    """
    Mealie uses naive date times since the app handles timezones explicitly.
    All timezones are generated, stored, and retrieved as UTC.

    This class strips the timezone from a datetime object when storing it so the database (i.e. postgres)
    doesn't do any timezone conversion when storing the datetime, then re-inserts UTC when retrieving it.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect):
        if value is None:
            return value

        try:
            if value.tzinfo is not None:
                value = value.astimezone(UTC)
            return value.replace(tzinfo=None)
        except Exception:
            return value

    def process_result_value(self, value: datetime | None, dialect):
        try:
            if value is not None:
                value = value.replace(tzinfo=UTC)
        except Exception:
            pass

        return value
