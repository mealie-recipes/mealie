from mealie.pkgs.stats import fs_stats
from mealie.schema._mealie import MealieModel


class GroupStatistics(MealieModel):
    total_recipes: int
    total_users: int
    total_categories: int
    total_tags: int
    total_tools: int


class GroupStorage(MealieModel):
    used_storage_bytes: int
    used_storage_str: str
    total_storage_bytes: int
    total_storage_str: str

    @classmethod
    def bytes(cls, used_storage_bytes: int, total_storage_bytes: int) -> "GroupStorage":
        return cls(
            used_storage_bytes=used_storage_bytes,
            used_storage_str=fs_stats.pretty_size(used_storage_bytes),
            total_storage_bytes=total_storage_bytes,
            total_storage_str=fs_stats.pretty_size(total_storage_bytes),
        )
