import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class JsonProvider:
    translations: dict

    def __init__(self, path: Path | dict):
        if isinstance(path, Path):
            self.translations = json.loads(path.read_text())
        else:
            self.translations = path

    def t(self, key: str, default=None, **kwargs) -> str:
        keys = key.split(".")

        translation_value: dict | str = self.translations
        last = len(keys) - 1

        for i, k in enumerate(keys):
            if k not in translation_value:
                break

            try:
                translation_value = translation_value[k]  # type: ignore
            except Exception:
                break

            if i == last:
                return translation_value

        return default or key
