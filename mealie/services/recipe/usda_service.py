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

# Standard nutrient numbers used by FoodData Central (consistent across data types)
_NUTRIENT_MAP: dict[str, str] = {
    "208": "calories",              # Energy (kcal)
    "203": "protein_content",      # Protein (g)
    "204": "fat_content",          # Total lipid/fat (g)
    "205": "carbohydrate_content", # Carbohydrate by difference (g)
    "291": "fiber_content",        # Fiber, total dietary (g)
    "269": "sugar_content",        # Sugars, total (g)
    "307": "sodium_content",       # Sodium (mg)
    "606": "saturated_fat_content",   # Fatty acids, total saturated (g)
    "601": "cholesterol_content",  # Cholesterol (mg)
    "605": "trans_fat_content",    # Fatty acids, total trans (g)
    # Unsaturated = mono + poly — handled specially below
    "645": "_mono_fat",            # Fatty acids, monounsaturated (g)
    "646": "_poly_fat",            # Fatty acids, polyunsaturated (g)
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
    """Extract mapped nutrients from a FDC food nutrient list."""
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

    # Compute unsaturated fat = mono + poly
    mono = values.pop("_mono_fat", None)
    poly = values.pop("_poly_fat", None)
    if mono is not None or poly is not None:
        values["unsaturated_fat_content"] = (mono or 0.0) + (poly or 0.0)

    return UsdaNutrition(**values)


def search_foods(query: str, api_key: str, page_size: int = 8) -> list[UsdaFoodSummary]:
    """Search FDC for foods matching *query*.

    Returns up to *page_size* results ordered by USDA relevance.
    Prefers Foundation and SR Legacy data types for accuracy.
    """
    # Pass dataType as a list so requests repeats the parameter
    # (?dataType=Foundation&dataType=SR+Legacy&...) rather than encoding
    # commas as %2C, which the USDA API rejects with a 400.
    params = [
        ("query", query),
        ("pageSize", page_size),
        ("dataType", "Foundation"),
        ("dataType", "SR Legacy"),
        ("dataType", "Survey (FNDDS)"),
        ("api_key", api_key),
    ]
    try:
        resp = requests.get(f"{USDA_BASE_URL}/foods/search", params=params, timeout=_TIMEOUT)
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
    """Fetch full nutrient data for a specific FDC food ID.

    Returns a :class:`UsdaNutrition` with values per 100g (or None for missing fields).
    """
    params = {"api_key": api_key}
    try:
        resp = requests.get(f"{USDA_BASE_URL}/food/{fdc_id}", params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("USDA FDC fetch request failed for fdcId=%s: %s", fdc_id, exc)
        raise RuntimeError(f"USDA request failed: {exc}") from exc

    data = resp.json()
    food_nutrients = data.get("foodNutrients", [])

    # Food detail endpoint nests the nutrient number differently
    normalized: list[dict] = []
    for fn in food_nutrients:
        nutrient = fn.get("nutrient", {})
        normalized.append(
            {
                "nutrientNumber": nutrient.get("number", ""),
                "value": fn.get("amount"),
            }
        )

    return _parse_nutrients(normalized)
