from ._base import RoutesBase, v1


class Users(RoutesBase):
    base = v1("/users")
    self = f"{base}/self"
