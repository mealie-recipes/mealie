from pydantic import UUID4


class RoutesBase:
    prefix = "/api"
    base = f"{prefix}/"

    def __init__(self) -> None:
        raise Exception("This class is not meant to be instantiated.")

    @classmethod
    def item(cls, item_id: int | str | UUID4) -> str:
        return f"{cls.base}/{item_id}"


class RoutesFoods(RoutesBase):
    base = "/api/foods"


class RoutesUnits(RoutesBase):
    base = "/api/units"


class RoutesOrganizerBase(RoutesBase):
    @classmethod
    def slug(cls, slug: str) -> str:
        return f"{cls.base}/slug/{slug}"


class RoutesTools(RoutesOrganizerBase):
    base = "/api/tools"


class RoutesTags(RoutesOrganizerBase):
    base = "/api/tags"


class RoutesCategory(RoutesOrganizerBase):
    base = "/api/categories"


class RoutesRecipe(RoutesBase):
    base = "/api/recipes"
