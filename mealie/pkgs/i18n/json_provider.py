import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast


@dataclass(slots=True)
class JsonProvider:
    translations: dict

    def __init__(self, path: Path | dict):
        if isinstance(path, Path):
            self.translations = json.loads(path.read_text())
        else:
            self.translations = path

    def _parse_plurals(self, value: str, count: float):
        # based off of: https://kazupon.github.io/vue-i18n/guide/pluralization.html

        values = [v.strip() for v in value.split("|")]
        if len(values) == 1:
            return value
        elif len(values) == 2:
            return values[0] if count == 1 else values[1]
        elif len(values) == 3:
            if count == 0:
                return values[0]
            else:
                return values[1] if count == 1 else values[2]
        else:
            return values[0]

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
                for key, value in kwargs.items():
                    translation_value = cast(str, translation_value)
                    if value is None:
                        value = ""
                    if key == "count":
                        translation_value = self._parse_plurals(translation_value, float(value))
                    translation_value = translation_value.replace("{" + key + "}", str(value))  # type: ignore
                return translation_value  # type: ignore

        return default or key
