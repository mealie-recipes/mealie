"""Service for calculating per-serving nutritional information from recipe ingredients.

Calculation approach:
- Food nutrition is stored per 100g.
- For each ingredient the effective weight in grams is determined from its unit:
    - GRAM / KILOGRAM / OUNCE / POUND units → convert directly to grams.
    - No unit (or unrecognised unit) + food has serving_weight_g → quantity × serving_weight_g.
    - Otherwise the ingredient is skipped (no reliable gram conversion).
- Nutrient totals are divided by the number of servings to yield per-serving values.
- Ingredients whose note indicates they are used for frying (e.g. "for frying",
  "for deep frying") are skipped — most of the oil stays in the pan and is not
  consumed.
"""

from __future__ import annotations

import re

from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import IngredientFood, IngredientUnit, StandardizedUnitType
from mealie.schema.recipe.recipe_nutrition import Nutrition

# Matches ingredient notes that indicate the ingredient is used for frying
# (and therefore most of it is not consumed).  Examples: "for frying",
# "for deep frying", "for pan frying", "to fry", "for deep-frying".
_FRYING_NOTE_RE = re.compile(
    r"\b(for\s+)?(deep[- ])?fry(ing)?\b"
    r"|\bfor\s+pan[- ]fry(ing)?\b"
    r"|\bfor\s+shallow[- ]fry(ing)?\b",
    re.IGNORECASE,
)

# Grams per one unit of each weight-based StandardizedUnitType
_GRAMS_PER_STANDARD_UNIT: dict[str, float] = {
    StandardizedUnitType.GRAM: 1.0,
    StandardizedUnitType.KILOGRAM: 1000.0,
    StandardizedUnitType.OUNCE: 28.3495,
    StandardizedUnitType.POUND: 453.592,
}

_NUTRITION_FIELDS = (
    "calories",
    "protein_content",
    "fat_content",
    "carbohydrate_content",
    "fiber_content",
    "sugar_content",
    "sodium_content",
    "saturated_fat_content",
    "cholesterol_content",
    "trans_fat_content",
    "unsaturated_fat_content",
)


def _ingredient_weight_g(quantity: float, unit: IngredientUnit | None, food: IngredientFood) -> float | None:
    """Return the weight in grams of this ingredient, or None if it cannot be determined."""
    if unit and unit.standard_unit and unit.standard_quantity:
        grams_per_standard = _GRAMS_PER_STANDARD_UNIT.get(unit.standard_unit)
        if grams_per_standard is not None:
            return quantity * unit.standard_quantity * grams_per_standard

    # Fall back to per-item weight on the food itself (e.g. "1 egg = 50g")
    if food.serving_weight_g and food.serving_weight_g > 0:
        return quantity * food.serving_weight_g

    return None


def _food_has_nutrition(food: IngredientFood) -> bool:
    return any(getattr(food, field) is not None for field in _NUTRITION_FIELDS)


def _is_frying_ingredient(note: str | None) -> bool:
    """Return True if the ingredient note indicates it is used for frying."""
    return bool(note and _FRYING_NOTE_RE.search(note))


def calculate_recipe_nutrition(recipe: Recipe) -> Nutrition | None:
    """Calculate per-serving nutrition for *recipe* from its ingredient food data.

    Returns a ``Nutrition`` instance (fields as strings, matching the existing
    recipe nutrition schema) or ``None`` if no ingredients have nutrition data.
    """
    servings = recipe.recipe_servings or 1

    totals: dict[str, float] = {field: 0.0 for field in _NUTRITION_FIELDS}
    any_data = False

    for ingredient in recipe.recipe_ingredient:
        food = ingredient.food
        quantity = ingredient.quantity

        # Skip section headers and ingredients without food or quantity
        if not food or not quantity or not isinstance(food, IngredientFood):
            continue

        # Skip oils/fats used for frying — most stays in the pan and is not consumed
        if _is_frying_ingredient(ingredient.note):
            continue

        if not _food_has_nutrition(food):
            continue

        weight_g = _ingredient_weight_g(quantity, ingredient.unit, food)
        if weight_g is None or weight_g <= 0:
            continue

        factor = weight_g / 100.0

        for field in _NUTRITION_FIELDS:
            value = getattr(food, field)
            if value is not None:
                totals[field] += value * factor
                any_data = True

    if not any_data:
        return None

    per_serving: dict[str, str | None] = {}
    for field in _NUTRITION_FIELDS:
        total = totals[field]
        per_serving_val = total / servings
        # Round to 1 decimal place and store as string (matching schema.org / existing Nutrition model)
        per_serving[field] = f"{per_serving_val:.1f}" if per_serving_val else None

    # Map food nutrition field names to Nutrition schema field names
    # (they share the same names except calories which maps directly)
    return Nutrition(
        calories=per_serving.get("calories"),
        carbohydrate_content=per_serving.get("carbohydrate_content"),
        cholesterol_content=per_serving.get("cholesterol_content"),
        fat_content=per_serving.get("fat_content"),
        fiber_content=per_serving.get("fiber_content"),
        protein_content=per_serving.get("protein_content"),
        saturated_fat_content=per_serving.get("saturated_fat_content"),
        sodium_content=per_serving.get("sodium_content"),
        sugar_content=per_serving.get("sugar_content"),
        trans_fat_content=per_serving.get("trans_fat_content"),
        unsaturated_fat_content=per_serving.get("unsaturated_fat_content"),
    )
