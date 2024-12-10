"""
From Pydantic V1: https://github.com/pydantic/pydantic/blob/abcf81ec104d2da70894ac0402ae11a7186c5e47/pydantic/datetime_parse.py
"""

import re
from datetime import UTC, date, datetime, time, timedelta, timezone

date_expr = r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})"
time_expr = (
    r"(?P<hour>\d{1,2}):(?P<minute>\d{1,2})"
    r"(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?"
    r"(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$"
)

date_re = re.compile(f"{date_expr}$")
time_re = re.compile(time_expr)
datetime_re = re.compile(f"{date_expr}[T ]{time_expr}")

standard_duration_re = re.compile(
    r"^"
    r"(?:(?P<days>-?\d+) (days?, )?)?"
    r"((?:(?P<hours>-?\d+):)(?=\d+:\d+))?"
    r"(?:(?P<minutes>-?\d+):)?"
    r"(?P<seconds>-?\d+)"
    r"(?:\.(?P<microseconds>\d{1,6})\d{0,6})?"
    r"$"
)

# Support the sections of ISO 8601 date representation that are accepted by timedelta
iso8601_duration_re = re.compile(
    r"^(?P<sign>[-+]?)"
    r"P"
    r"(?:(?P<days>\d+(.\d+)?)D)?"
    r"(?:T"
    r"(?:(?P<hours>\d+(.\d+)?)H)?"
    r"(?:(?P<minutes>\d+(.\d+)?)M)?"
    r"(?:(?P<seconds>\d+(.\d+)?)S)?"
    r")?"
    r"$"
)

EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
# if greater than this, the number is in ms, if less than or equal it's in seconds
# (in seconds this is 11th October 2603, in ms it's 20th August 1970)
MS_WATERSHED = int(2e10)
# slightly more than datetime.max in ns - (datetime.max - EPOCH).total_seconds() * 1e9
MAX_NUMBER = int(3e20)


class DateError(ValueError):
    def __init__(self, *args: object) -> None:
        super().__init__("invalid date format")


class TimeError(ValueError):
    def __init__(self, *args: object) -> None:
        super().__init__("invalid time format")


class DateTimeError(ValueError):
    def __init__(self, *args: object) -> None:
        super().__init__("invalid datetime format")


class DurationError(ValueError):
    def __init__(self, *args: object) -> None:
        super().__init__("invalid duration format")


def get_numeric(value: str | bytes | int | float, native_expected_type: str) -> None | int | float:
    if isinstance(value, int | float):
        return value
    try:
        return float(value)
    except ValueError:
        return None
    except TypeError as e:
        raise TypeError(f"invalid type; expected {native_expected_type}, string, bytes, int or float") from e


def from_unix_seconds(seconds: int | float) -> datetime:
    if seconds > MAX_NUMBER:
        return datetime.max
    elif seconds < -MAX_NUMBER:
        return datetime.min

    while abs(seconds) > MS_WATERSHED:
        seconds /= 1000
    dt = EPOCH + timedelta(seconds=seconds)
    return dt.replace(tzinfo=UTC)


def _parse_timezone(value: str | None, error: type[Exception]) -> None | int | timezone:
    if value == "Z":
        return UTC
    elif value is not None:
        offset_mins = int(value[-2:]) if len(value) > 3 else 0
        offset = 60 * int(value[1:3]) + offset_mins
        if value[0] == "-":
            offset = -offset
        try:
            return timezone(timedelta(minutes=offset))
        except ValueError as e:
            raise error() from e
    else:
        return None


def parse_date(value: date | str | bytes | int | float) -> date:
    """
    Parse a date/int/float/string and return a datetime.date.

    Raise ValueError if the input is well formatted but not a valid date.
    Raise ValueError if the input isn't well formatted.
    """
    if isinstance(value, date):
        if isinstance(value, datetime):
            return value.date()
        else:
            return value

    number = get_numeric(value, "date")
    if number is not None:
        return from_unix_seconds(number).date()

    if isinstance(value, bytes):
        value = value.decode()

    match = date_re.match(value)  # type: ignore
    if match is None:
        raise DateError()

    kw = {k: int(v) for k, v in match.groupdict().items()}

    try:
        return date(**kw)
    except ValueError as e:
        raise DateError() from e


def parse_time(value: time | str | bytes | int | float) -> time:
    """
    Parse a time/string and return a datetime.time.

    Raise ValueError if the input is well formatted but not a valid time.
    Raise ValueError if the input isn't well formatted, in particular if it contains an offset.
    """
    if isinstance(value, time):
        return value

    number = get_numeric(value, "time")
    if number is not None:
        if number >= 86400:
            # doesn't make sense since the time time loop back around to 0
            raise TimeError()
        return (datetime.min + timedelta(seconds=number)).time()

    if isinstance(value, bytes):
        value = value.decode()

    match = time_re.match(value)  # type: ignore
    if match is None:
        raise TimeError()

    kw = match.groupdict()
    if kw["microsecond"]:
        kw["microsecond"] = kw["microsecond"].ljust(6, "0")

    tzinfo = _parse_timezone(kw.pop("tzinfo"), TimeError)
    kw_: dict[str, None | int | timezone] = {k: int(v) for k, v in kw.items() if v is not None}
    kw_["tzinfo"] = tzinfo

    try:
        return time(**kw_)  # type: ignore
    except ValueError as e:
        raise TimeError() from e


def parse_datetime(value: datetime | str | bytes | int | float) -> datetime:
    """
    Parse a datetime/int/float/string and return a datetime.datetime.

    This function supports time zone offsets. When the input contains one,
    the output uses a timezone with a fixed offset from UTC.

    Raise ValueError if the input is well formatted but not a valid datetime.
    Raise ValueError if the input isn't well formatted.
    """
    if isinstance(value, datetime):
        return value

    number = get_numeric(value, "datetime")
    if number is not None:
        return from_unix_seconds(number)

    if isinstance(value, bytes):
        value = value.decode()

    match = datetime_re.match(value)  # type: ignore
    if match is None:
        raise DateTimeError()

    kw = match.groupdict()
    if kw["microsecond"]:
        kw["microsecond"] = kw["microsecond"].ljust(6, "0")

    tzinfo = _parse_timezone(kw.pop("tzinfo"), DateTimeError)
    kw_: dict[str, None | int | timezone] = {k: int(v) for k, v in kw.items() if v is not None}
    kw_["tzinfo"] = tzinfo

    try:
        return datetime(**kw_)  # type: ignore # noqa DTZ001
    except ValueError as e:
        raise DateTimeError() from e


def parse_duration(value: str | bytes | int | float) -> timedelta:
    """
    Parse a duration int/float/string and return a datetime.timedelta.

    The preferred format for durations in Django is '%d %H:%M:%S.%f'.

    Also supports ISO 8601 representation.
    """
    if isinstance(value, timedelta):
        return value

    if isinstance(value, int | float):
        # below code requires a string
        value = f"{value:f}"
    elif isinstance(value, bytes):
        value = value.decode()

    try:
        match = standard_duration_re.match(value) or iso8601_duration_re.match(value)
    except TypeError as e:
        raise TypeError("invalid type; expected timedelta, string, bytes, int or float") from e

    if not match:
        raise DurationError()

    kw = match.groupdict()
    sign = -1 if kw.pop("sign", "+") == "-" else 1
    if kw.get("microseconds"):
        kw["microseconds"] = kw["microseconds"].ljust(6, "0")

    if kw.get("seconds") and kw.get("microseconds") and kw["seconds"].startswith("-"):
        kw["microseconds"] = "-" + kw["microseconds"]

    kw_ = {k: float(v) for k, v in kw.items() if v is not None}

    return sign * timedelta(**kw_)
