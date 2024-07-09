from datetime import datetime, timezone


def get_utc_now():
    """
    Returns the current time in UTC.
    """
    return datetime.now(timezone.utc)


def get_utc_today():
    """
    Returns the current date in UTC.
    """
    return datetime.now(timezone.utc).date()
