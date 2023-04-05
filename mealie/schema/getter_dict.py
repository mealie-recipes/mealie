from collections.abc import Callable, Mapping
from typing import Any

from pydantic.utils import GetterDict


class CustomGetterDict(GetterDict):
    transformations: Mapping[str, Callable[[Any], Any]]

    def get(self, key: Any, default: Any = None) -> Any:
        # Transform extras into key-value dict
        if key in self.transformations:
            value = super().get(key, default)
            return self.transformations[key](value)

        # Keep all other fields as they are
        else:
            return super().get(key, default)


class ExtrasGetterDict(CustomGetterDict):
    transformations = {"extras": lambda value: {x.key_name: x.value for x in value}}


class GroupGetterDict(CustomGetterDict):
    transformations = {"group": lambda value: value.name}


class UserGetterDict(CustomGetterDict):
    transformations = {
        "group": lambda value: value.name,
        "favorite_recipes": lambda value: [x.slug for x in value],
    }
