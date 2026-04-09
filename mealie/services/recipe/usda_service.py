"""Client for the USDA FoodData Central (FDC) API.

Docs: https://fdc.nal.usda.gov/api-guide.html
Free API keys: https://fdc.nal.usda.gov/api-key-signup.html

All nutrient values returned by FDC are per 100g of food.
"""

from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)

USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"
_TIMEOUT = 10  # seconds

# Standard nutrient numbers used by FoodData Central (consistent across data types).
# These are the numbers passed to the ?nutrients= filter on the detail endpoint.
_NUTRIENT_NUMBERS = [203, 204, 205, 208, 269, 291, 307, 601, 605, 606, 645, 646]

# Maps FDC nutrient number (string) → Mealie food field name
_NUTRIENT_MAP: dict[str, str] = {
    "208": "calories",                # Energy (kcal)
    "203": "protein_content",         # Protein (g)
    "204": "fat_content",             # Total lipid/fat (g)
    "205": "carbohydrate_content",    # Carbohydrate by difference (g)
    "291": "fiber_content",           # Fiber, total dietary (g)
    "269": "sugar_content",           # Sugars, total (g)
    "307": "sodium_content",          # Sodium (mg)
    "606": "saturated_fat_content",   # Fatty acids, total saturated (g)
    "601": "cholesterol_content",     # Cholesterol (mg)
    "605": "trans_fat_content",       # Fatty acids, total trans (g)
    # Unsaturated = mono + poly — handled specially below
    "645": "_mono_fat",               # Fatty acids, monounsaturated (g)
    "646": "_poly_fat",               # Fatty acids, polyunsaturated (g)
}


class UsdaFoodSummary:
    """Lightweight search result from FDC."""

    def __init__(self, fdc_id: int, description: str, brand_owner: str | None = None) -> None:
        self.fdc_id = fdc_id
        self.description = description
        self.brand_owner = brand_owner


class UsdaNutrition:
    """Nutrition values per 100g from FDC, mapped to Mealie field names."""

    def __init__(self, **kwargs: float | None) -> None:
        self.calories: float | None = kwargs.get("calories")
        self.protein_content: float | None = kwargs.get("protein_content")
        self.fat_content: float | None = kwargs.get("fat_content")
        self.carbohydrate_content: float | None = kwargs.get("carbohydrate_content")
        self.fiber_content: float | None = kwargs.get("fiber_content")
        self.sugar_content: float | None = kwargs.get("sugar_content")
        self.sodium_content: float | None = kwargs.get("sodium_content")
        self.saturated_fat_content: float | None = kwargs.get("saturated_fat_content")
        self.cholesterol_content: float | None = kwargs.get("cholesterol_content")
        self.trans_fat_content: float | None = kwargs.get("trans_fat_content")
        self.unsaturated_fat_content: float | None = kwargs.get("unsaturated_fat_content")


def _parse_nutrients(food_nutrients: list[dict]) -> UsdaNutrition:
    """Extract mapped nutrients from a normalised FDC nutrient list.

    Each entry must have ``nutrientNumber`` (str) and ``value`` (float).
    """
    values: dict[str, float] = {}
    for nutrient in food_nutrients:
        number = str(nutrient.get("nutrientNumber", ""))
        value = nutrient.get("value")
        if value is None:
            continue
        try:
            float_val = float(value)
        except (TypeError, ValueError):
            continue
        mapped = _NUTRIENT_MAP.get(number)
        if mapped:
            values[mapped] = float_val

    # Unsaturated fat = monounsaturated + polyunsaturated
    mono = values.pop("_mono_fat", None)
    poly = values.pop("_poly_fat", None)
    if mono is not None or poly is not None:
        values["unsaturated_fat_content"] = (mono or 0.0) + (poly or 0.0)

    return UsdaNutrition(**values)


def search_foods(query: str, api_key: str, page_size: int = 8) -> list[UsdaFoodSummary]:
    """Search FDC for foods matching *query*.

    Uses POST so that ``dataType`` is sent as a proper JSON array, avoiding the
    400 error that occurs when ``requests`` percent-encodes a comma-separated
    string in a GET query parameter.

    Returns up to *page_size* results ordered by USDA relevance, filtered to
    Foundation, SR Legacy, and Survey (FNDDS) data types for accuracy.
    """
    payload = {
        "query": query,
        "pageSize": page_size,
        "dataType": ["Foundation", "SR Legacy", "Survey (FNDDS)"],
    }
    try:
        resp = requests.post(
            f"{USDA_BASE_URL}/foods/search",
            json=payload,
            params={"api_key": api_key},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("USDA FDC search request failed: %s", exc)
        raise RuntimeError(f"USDA request failed: {exc}") from exc

    data = resp.json()
    results: list[UsdaFoodSummary] = []
    for food in data.get("foods", []):
        fdc_id = food.get("fdcId")
        description = food.get("description", "")
        brand = food.get("brandOwner") or food.get("brandName")
        if fdc_id and description:
            results.append(UsdaFoodSummary(fdc_id=int(fdc_id), description=description, brand_owner=brand))
    return results


def fetch_nutrition(fdc_id: int, api_key: str) -> UsdaNutrition:
    """Fetch nutrient data (per 100g) for a specific FDC food ID.

    Requests only the nutrient numbers we map, using repeating ``nutrients``
    query params as the spec allows (nutrients=203&nutrients=204&...).

    The detail endpoint returns ``FoodNutrient`` objects where the value is
    ``amount`` (top-level) and the nutrient number is ``nutrient.number``
    (nested string).
    """
    params = [("api_key", api_key)] + [("nutrients", n) for n in _NUTRIENT_NUMBERS]
    try:
        resp = requests.get(f"{USDA_BASE_URL}/food/{fdc_id}", params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("USDA FDC fetch request failed for fdcId=%s: %s", fdc_id, exc)
        raise RuntimeError(f"USDA request failed: {exc}") from exc

    data = resp.json()
    food_nutrients = data.get("foodNutrients", [])

    # Normalise FoodNutrient → {nutrientNumber, value} for _parse_nutrients
    normalized: list[dict] = []
    for fn in food_nutrients:
        nutrient = fn.get("nutrient", {})
        normalized.append(
            {
                "nutrientNumber": nutrient.get("number", ""),  # nested string, e.g. "203"
                "value": fn.get("amount"),                     # top-level float
            }
        )

    return _parse_nutrients(normalized)
