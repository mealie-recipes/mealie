from pydantic import BaseModel
from rapidfuzz import fuzz, process


def find_match[T: BaseModel](match_value: str, *, store_map: dict[str, T], fuzzy_match_threshold: int = 0) -> T | None:
    """Looks up a value in a store, falling back to the closest fuzzy match above the threshold."""

    # check for literal matches
    if match_value in store_map:
        return store_map[match_value]

    # fuzzy match against the store
    fuzz_result = process.extractOne(
        match_value, store_map.keys(), scorer=fuzz.ratio, score_cutoff=fuzzy_match_threshold
    )
    if fuzz_result is None:
        return None

    return store_map[fuzz_result[0]]
