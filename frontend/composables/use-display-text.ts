/**
 * use-display-text module contains helpful utility functions to compute the display text when provided
 * with the food, units, quantity, and notes.
 */

import { IngredientFood, IngredientUnit } from "~/types/api-types/recipe";

export function getDisplayText(
  notes = "",
  quantity: number | null = null,
  food: IngredientFood | null = null,
  unit: IngredientUnit | null = null
): string {
  // Fallback to note only if no food or unit is provided
  if (food === null && unit === null) {
    return `${quantity || ""} ${notes}`.trim();
  }

  // Otherwise build the display text
  let displayText = "";

  if (quantity) {
    displayText += quantity;
  }

  if (unit) {
    displayText += ` ${unit.name}`;
  }

  if (food) {
    displayText += ` ${food.name}`;
  }

  if (notes) {
    displayText += ` ${notes}`;
  }

  return displayText.trim();
}
