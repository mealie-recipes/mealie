from collections.abc import Callable
from typing import Optional

from pydantic import BaseModel


class MigrationAlias(BaseModel):
    """A datatype used by MigrationBase to pre-process a recipe dictionary to rewrite
    the alias key in the dictionary, if it exists, to the key. If set a `func` attribute
    will be called on the value before assigning the value to the new key
    """

    key: str
    alias: str
    func: Optional[Callable] = None
