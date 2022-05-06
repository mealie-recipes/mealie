from ._base import RoutesBase, v1


class Seeders(RoutesBase):
    base = v1("/groups/seeders")

    foods = f"{base}/foods"
    units = f"{base}/units"
    labels = f"{base}/labels"
