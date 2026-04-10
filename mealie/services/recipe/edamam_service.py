"""Client for the Edamam Food Database API (v2).

Docs: https://developer.edamam.com/food-database-api-docs
Authentication: ``app_id`` and ``app_key`` as query parameters.

The parser endpoint returns per-100g nutrient values for every result, so a
separate "nutrients" call is not required for our use case.
"""

from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)

EDAMAM_PARSER_URL = "https://api.edamam.com/api/food-database/v2/parser"
_TIMEOUT = 10  # seconds


class EdamamFood:
    """A food item returned by the Edamam parser with embedded per-100g nutrition."""

    def __init__(
        self,
        food_id: str,
        label: str,
        brand: str | None = None,
        category: str | None = None,
        nutrients_raw: dict[str, float] | None = None,
    ) -> None:
        self.food_id = food_id
        self.label = label
        self.brand = brand
        self.category = category
        self._n = nutrients_raw or {}

    # ── per-100g accessors ────────────────────────────────────────────────────
    # Edamam nutrient codes: https://developer.edamam.com/food-database-api-docs
    @property
    def calories(self) -> float | None:
        return self._n.get("ENERC_KCAL")

    @property
    def protein_content(self) -> float | None:
        return self._n.get("PROCNT")

    @property
    def fat_content(self) -> float | None:
        return self._n.get("FAT")

    @property
    def carbohydrate_content(self) -> float | None:
        return self._n.get("CHOCDF")

    @property
    def fiber_content(self) -> float | None:
        return self._n.get("FIBTG")

    @property
    def sugar_content(self) -> float | None:
        return self._n.get("SUGAR")

    @property
    def sodium_content(self) -> float | None:
        return self._n.get("NA")

    @property
    def saturated_fat_content(self) -> float | None:
        return self._n.get("FASAT")

    @property
    def cholesterol_content(self) -> float | None:
        return self._n.get("CHOLE")

    @property
    def trans_fat_content(self) -> float | None:
        return self._n.get("FATRN")

    @property
    def unsaturated_fat_content(self) -> float | None:
        mono = self._n.get("FAMS")
        poly = self._n.get("FAPU")
        if mono is None and poly is None:
            return None
        return (mono or 0.0) + (poly or 0.0)


def search_foods(query: str, app_id: str, app_key: str, page_size: int = 10) -> list[EdamamFood]:
    """Search the Edamam Food Database for foods matching *query*.

    Uses the ``logging`` nutrition-type so a wide range of foods is returned
    even without a quantity.  Per-100g nutrient values are embedded in each
    result — no second API call is needed.
    """
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "ingr": query,
        "nutrition-type": "logging",
    }
    try:
        resp = requests.get(EDAMAM_PARSER_URL, params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Edamam parser request failed: %s", exc)
        raise RuntimeError(f"Edamam request failed: {exc}") from exc

    data = resp.json()
    results: list[EdamamFood] = []
    for hint in data.get("hints", []):
        food = hint.get("food", {})
        food_id = food.get("foodId")
        label = food.get("label") or ""
        if not food_id or not label:
            continue
        results.append(
            EdamamFood(
                food_id=food_id,
                label=label,
                brand=food.get("brand"),
                category=food.get("category"),
                nutrients_raw=food.get("nutrients") or {},
            )
        )
        if len(results) >= page_size:
            break

    return results
