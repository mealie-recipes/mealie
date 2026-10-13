import re
from functools import lru_cache


@lru_cache
def compile_path(path: str) -> re.Pattern[str]:
    parts = re.split(r"({[^}]+})", path)
    pattern = ""
    for part in parts:
        if part.startswith("{"):
            name, _, converter = part[1:-1].partition(":")
            pattern += f"(?P<{name}>" + (".*" if converter == "path" else "[^/]+") + ")"
        else:
            pattern += re.escape(part)
    return re.compile("^" + pattern + "$")
