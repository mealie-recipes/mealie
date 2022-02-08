from pydantic import UUID4


class _RoutesBase:
    prefix = "/api"
    base = f"{prefix}/"

    def __init__(self) -> None:
        raise Exception("This class is not meant to be instantiated.")

    @classmethod
    def item(cls, item_id: int | str | UUID4) -> str:
        return f"{cls.base}/{item_id}"


class RoutesFoods(_RoutesBase):
    base = "/api/foods"


class RoutesUnits(_RoutesBase):
    base = "/api/units"
