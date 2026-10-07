import hashlib
import json
import unicodedata
from typing import Any

from mealie.schema.recipe import Recipe

CONTENT_FIELDS = {
    "name",
    "description",
    "recipe_ingredient",
    "recipe_instructions",
    "recipe_yield",
    "recipe_yield_quantity",
    "recipe_servings",
    "total_time",
    "prep_time",
    "perform_time",
    "total_time_seconds",
    "prep_time_seconds",
    "perform_time_seconds",
    "nutrition",
    "notes",
}


def _normalize(value: Any) -> Any:
    if isinstance(value, str):
        return " ".join(unicodedata.normalize("NFC", value).split())
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _normalize(item)
            for key, item in value.items()
            if key not in {"id", "reference_id", "created_at", "updated_at", "display"} and not key.endswith("_id")
        }
    return value


def recipe_fingerprint(recipe: Recipe) -> str:
    """Versioned content identity, independent of archive paths and generated IDs.

    Tags, ratings, ownership, images and import timestamps are deliberately excluded.
    Preserve case, ingredient/instruction order and quantities to avoid merging distinct recipes.
    """
    content = _normalize(recipe.model_dump(mode="json", include=CONTENT_FIELDS))
    encoded = json.dumps({"version": 1, "content": content}, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()
