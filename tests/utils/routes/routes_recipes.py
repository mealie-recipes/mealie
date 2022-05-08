from ._base import RoutesBase, v1


class Foods(RoutesBase):
    base = v1("/foods")


class Units(RoutesBase):
    base = v1("/units")


class Recipe(RoutesBase):
    base = v1("/recipes")
