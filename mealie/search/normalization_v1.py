"""Version 1 search normalization. Preserve this contract for index migrations."""

import re
import unicodedata

LIGATURES = {"ß": "ss", "æ": "ae", "œ": "oe", "ø": "o", "ł": "l", "đ": "d", "þ": "th", "ς": "σ"}
COMBINING_MARKS = "".join(chr(code) for code in range(0x110000) if unicodedata.combining(chr(code)))
_REMOVE_MARKS = str.maketrans("", "", COMBINING_MARKS)


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).translate(_REMOVE_MARKS).lower()
    for source, replacement in LIGATURES.items():
        value = value.replace(source, replacement)
    return " ".join(re.findall(r"[^\W_]+", value))
