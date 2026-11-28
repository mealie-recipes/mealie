"""Database-independent recipe search syntax and token policy."""

from dataclasses import dataclass
from typing import Literal

from rapidfuzz.distance import Levenshtein

from .normalization_v1 import normalize

SearchMode = Literal["all", "any"]


@dataclass(frozen=True)
class Clause:
    text: str
    kind: Literal["ordinary", "required", "excluded", "phrase"] = "ordinary"

    @property
    def alternatives(self) -> tuple[str, ...]:
        if self.kind != "ordinary":
            return (self.text,)
        if self.text in {"lettuce wrap", "lettuce wraps", "lettuce cup", "lettuce cups"}:
            return ("lettuce wrap", "lettuce wraps", "lettuce cup", "lettuce cups")
        word = self.text
        if " " in word or len(word) < 3:
            return (word,)
        if word.endswith("ies"):
            return tuple(dict.fromkeys((word, word[:-3] + "y", word[:-1], word[:-2])))
        if word.endswith("es"):
            return (word, word[:-1], word[:-2])
        if word.endswith("s") and not word.endswith(("ss", "us")):
            return (word, word[:-1])
        if word.endswith("y") and word[-2] not in "aeiou":
            return (word, word[:-1] + "ies")
        if word.endswith(("o", "i")):
            return (word, word + "s", word + "es")
        if word.endswith(("s", "x", "z", "ch", "sh")):
            return (word, word + "es")
        return (word, word + "s")


@dataclass(frozen=True)
class SearchQuery:
    clauses: tuple[Clause, ...]
    mode: SearchMode = "all"

    @property
    def prefix(self) -> bool:
        return len(self.clauses) == 1 and self.clauses[0].kind == "ordinary" and " " not in self.clauses[0].text


def parse(search: str, mode: SearchMode = "all") -> SearchQuery:
    if mode not in ("all", "any"):
        raise ValueError("Invalid search mode")
    if len(search) > 512:
        raise ValueError("Search must contain at most 512 characters")
    clauses: list[Clause] = []
    position = 0
    while position < len(search):
        if search[position].isspace():
            position += 1
            continue
        sign = ""
        if search[position] in "+-":
            sign = search[position]
            position += 1
            if position == len(search) or search[position].isspace():
                raise ValueError("A search sign must precede a word or phrase")
        quoted = search[position] == '"'
        if quoted:
            end = search.find('"', position + 1)
            if end < 0:
                raise ValueError("Search has an unmatched double quote")
            value = search[position + 1 : end]
            position = end + 1
            if position < len(search) and not search[position].isspace():
                raise ValueError("Separate search clauses with spaces")
        else:
            end = position
            while end < len(search) and not search[end].isspace():
                if search[end] == '"':
                    raise ValueError("Separate quoted phrases with spaces")
                end += 1
            value = search[position:end]
            position = end
        value = normalize(value)
        if not value:
            if sign or quoted:
                raise ValueError("Search clauses must contain a word")
            continue
        kind: Literal["ordinary", "required", "excluded", "phrase"] = (
            "excluded" if sign == "-" else "required" if sign == "+" else "phrase" if quoted else "ordinary"
        )
        clauses.append(Clause(value, kind))
        if len(clauses) > 32:
            raise ValueError("Search must contain at most 32 clauses")
    merged: list[Clause] = []
    index = 0
    while index < len(clauses):
        clause = clauses[index]
        if index + 1 < len(clauses) and clause == Clause("lettuce"):
            following = clauses[index + 1]
            if following.kind == "ordinary" and following.text in {"wrap", "wraps", "cup", "cups"}:
                merged.append(Clause(f"lettuce {following.text}"))
                index += 2
                continue
        merged.append(clause)
        index += 1
    return SearchQuery(tuple(merged), mode)


def correction(word: str, vocabulary: set[str]) -> str | None:
    if len(word) < 5:
        return None
    matches = [candidate for candidate in vocabulary if Levenshtein.distance(word, candidate, score_cutoff=1) <= 1]
    return matches[0] if len(matches) == 1 else None
