from datetime import datetime
from enum import Enum
from typing import overload

from dateutil.relativedelta import relativedelta


class PlaceholderKeyword(Enum):
    NOW = "$NOW"

    @classmethod
    def _parse_now(cls, value: str) -> str:
        """
        Parses a NOW value, with optional math using an int or float.

        Operation:
            - '+'
            - '-'

        Unit:
            - 'y' (year)
            - 'm' (month)
            - 'd' (day)
            - 'H' (hour)
            - 'M' (minute)
            - 'S' (second)

        Examples:
            - '$NOW'
            - '$NOW+30d'
            - '$NOW-5M'
        """

        if not value.startswith(cls.NOW.value):
            return value

        now = datetime.now(tz=None)  # noqa: DTZ005
        remainder = value[len(cls.NOW.value) :]

        if remainder:
            if len(remainder) < 3:
                raise ValueError(f"Invalid remainder in NOW string ({value})")

            op = remainder[0]
            amount_str = remainder[1:-1]
            unit = remainder[-1]

            try:
                amount = int(amount_str)
            except Exception as e:
                raise ValueError(f"Invalid amount in NOW string ({value})") from e

            if op == "-":
                amount = -amount
            elif op != "+":
                raise ValueError(f"Invalid operator in NOW string ({value})")

            if unit == "y":
                delta = relativedelta(years=amount)
            elif unit == "m":
                delta = relativedelta(months=amount)
            elif unit == "d":
                delta = relativedelta(days=amount)
            elif unit == "H":
                delta = relativedelta(hours=amount)
            elif unit == "M":
                delta = relativedelta(minutes=amount)
            elif unit == "S":
                delta = relativedelta(seconds=amount)
            else:
                raise ValueError(f"Invalid time unit in NOW string ({value})")

            dt = now + delta

        else:
            dt = now

        return dt.isoformat()

    @overload
    @classmethod
    def parse_value(cls, value: str) -> str: ...

    @overload
    @classmethod
    def parse_value(cls, value: list[str]) -> list[str]: ...

    @overload
    @classmethod
    def parse_value(cls, value: None) -> None: ...

    @classmethod
    def parse_value(cls, value: str | list[str] | None) -> str | list[str] | None:
        if not value:
            return value

        if isinstance(value, list):
            return [cls.parse_value(v) for v in value]

        if value.startswith(PlaceholderKeyword.NOW.value):
            return cls._parse_now(value)

        return value


class RelationalKeyword(Enum):
    IS = "IS"
    IS_NOT = "IS NOT"
    IN = "IN"
    NOT_IN = "NOT IN"
    CONTAINS_ALL = "CONTAINS ALL"
    LIKE = "LIKE"
    NOT_LIKE = "NOT LIKE"

    @classmethod
    def parse_component(cls, component: str) -> list[str] | None:
        """
        Try to parse a component using a relational keyword

        If no matching keyword is found, returns None
        """

        # extract the attribute name from the component
        parsed_component = component.split(maxsplit=1)
        if len(parsed_component) < 2:
            return None

        # assume the component has already filtered out the value and try to match a keyword
        # if we try to filter out the value without checking first, keywords with spaces won't parse correctly
        possible_keyword = parsed_component[1].strip().lower()
        for rel_kw in sorted([keyword.value for keyword in cls], key=len, reverse=True):
            if rel_kw.lower() != possible_keyword:
                continue

            parsed_component[1] = rel_kw
            return parsed_component

        # there was no match, so the component may still have the value in it
        try:
            _possible_keyword, _value = parsed_component[-1].rsplit(maxsplit=1)
            parsed_component = [parsed_component[0], _possible_keyword, _value]
        except ValueError:
            # the component has no value to filter out
            return None

        possible_keyword = parsed_component[1].strip().lower()
        for rel_kw in sorted([keyword.value for keyword in cls], key=len, reverse=True):
            if rel_kw.lower() != possible_keyword:
                continue

            parsed_component[1] = rel_kw
            return parsed_component

        return None
