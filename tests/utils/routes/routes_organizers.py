from ._base import RoutesBase, v1


class RoutesOrganizerBase(RoutesBase):
    @classmethod
    def slug(cls, slug: str) -> str:
        return f"{cls.base}/slug/{slug}"


class Tools(RoutesOrganizerBase):
    base = v1("/organizers/tools")


class Tags(RoutesOrganizerBase):
    base = v1("/organizers/tags")


class Categories(RoutesOrganizerBase):
    base = v1("/organizers/categories")
