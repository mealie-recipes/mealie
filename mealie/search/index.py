"""Current recipe search index interface."""

from .index_v1 import install, rebuild, register_sqlite, segments, terms, uninstall

__all__ = ["install", "rebuild", "register_sqlite", "segments", "terms", "uninstall"]


def include_name(name: str | None, type_: str, parent_names: dict) -> bool:
    return type_ != "table" or name is None or not name.startswith("recipe_search_")
