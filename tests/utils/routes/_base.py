from pydantic import UUID4


def v1(route: str) -> str:
    return f"/api{route}"


class RoutesBase:
    prefix = "/api"
    base = f"{prefix}/"

    def __init__(self) -> None:
        raise NotImplementedError("This class is not meant to be instantiated.")

    @classmethod
    def item(cls, item_id: int | str | UUID4) -> str:
        return f"{cls.base}/{item_id}"
