from ._base import RoutesBase, v1


class AdminUsers(RoutesBase):
    base = v1("/admin/users")
