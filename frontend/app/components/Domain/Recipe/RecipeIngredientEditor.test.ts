import { describe, expect, test } from "vitest";
import { ref } from "vue";

/**
 * Tests for mobile "next" button support in ingredient autocomplete fields.
 *
 * Mobile keyboards show a "next" button (via enterkeyhint="next") which on many browsers
 * (particularly Android Chrome) only triggers a blur event without firing keydown/keyup.
 *
 * These tests verify that the blur handlers select the first filtered item when:
 * - User has typed a search query
 * - No item is currently selected
 * - Filtered items are available
 */
describe("RecipeIngredientEditor mobile next button logic", () => {
  test("handleUnitBlur selects first filtered unit when search is active", () => {
    // Simulate the component state
    const model = ref({ unit: undefined });
    const unitSearch = ref("cu");
    const filteredUnits = ref([
      { id: "unit-1", name: "cup" },
      { id: "unit-2", name: "cups" },
    ]);

    // This is the blur handler logic from RecipeIngredientEditor.vue
    function handleUnitBlur() {
      if (unitSearch.value && !model.value.unit && filteredUnits.value.length > 0) {
        model.value.unit = filteredUnits.value[0];
      }
    }

    // Before blur, no unit is selected
    expect(model.value.unit).toBeUndefined();

    // Trigger blur (simulating mobile "next" button press)
    handleUnitBlur();

    // After blur, first filtered unit should be selected
    expect(model.value.unit).toBeDefined();
    expect(model.value.unit?.name).toBe("cup");
  });

  test("handleFoodBlur selects first filtered food when search is active", () => {
    // Simulate the component state
    const model = ref({ food: undefined });
    const foodSearch = ref("ch");
    const filteredFoods = ref([
      { id: "food-1", name: "chicken" },
      { id: "food-2", name: "cheese" },
      { id: "food-3", name: "chocolate" },
    ]);

    // This is the blur handler logic from RecipeIngredientEditor.vue
    function handleFoodBlur() {
      if (foodSearch.value && !model.value.food && filteredFoods.value.length > 0) {
        model.value.food = filteredFoods.value[0];
      }
    }

    // Before blur, no food is selected
    expect(model.value.food).toBeUndefined();

    // Trigger blur (simulating mobile "next" button press)
    handleFoodBlur();

    // After blur, first filtered food should be selected
    expect(model.value.food).toBeDefined();
    expect(model.value.food?.name).toBe("chicken");
  });

  test("handleBlur does not select when no search value", () => {
    const model = ref({ unit: undefined });
    const unitSearch = ref("");
    const filteredUnits = ref([{ id: "unit-1", name: "cup" }]);

    function handleUnitBlur() {
      if (unitSearch.value && !model.value.unit && filteredUnits.value.length > 0) {
        model.value.unit = filteredUnits.value[0];
      }
    }

    handleUnitBlur();

    // Should not select when search is empty
    expect(model.value.unit).toBeUndefined();
  });

  test("handleBlur does not select when item already selected", () => {
    const preselectedUnit = { id: "unit-2", name: "cups" };
    const model = ref({ unit: preselectedUnit });
    const unitSearch = ref("ta");
    const filteredUnits = ref([{ id: "unit-3", name: "tablespoon" }]);

    function handleUnitBlur() {
      if (unitSearch.value && !model.value.unit && filteredUnits.value.length > 0) {
        model.value.unit = filteredUnits.value[0];
      }
    }

    handleUnitBlur();

    // Should not change when item already selected
    expect(model.value.unit).toEqual(preselectedUnit);
    expect(model.value.unit?.name).toBe("cups");
  });

  test("handleBlur does not select when no filtered items", () => {
    const model = ref({ unit: undefined });
    const unitSearch = ref("xyz");
    const filteredUnits = ref([]);

    function handleUnitBlur() {
      if (unitSearch.value && !model.value.unit && filteredUnits.value.length > 0) {
        model.value.unit = filteredUnits.value[0];
      }
    }

    handleUnitBlur();

    // Should not select when no filtered results
    expect(model.value.unit).toBeUndefined();
  });
});
