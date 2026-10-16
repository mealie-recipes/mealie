import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import MealPlanLayout from "./MealPlanLayout.vue";
import type { Days } from "~/composables/use-group-mealplan";
import type { ReadPlanEntry } from "~/lib/api/types/meal-plan";

describe("MealPlanLayout", () => {
  it.each([
    { types: [], sizes: [] },
    { types: ["breakfast", "breakfast", "lunch", "dinner"], sizes: [2, 1, 1] },
    { types: ["dinner", "breakfast", "dinner", "lunch"], sizes: [1, 1, 1, 1] },
  ])("preserves saved order and groups adjacent types: $types", ({ types, sizes }) => {
    const meals = types.map((entryType, id) => ({ id, entryType }) as ReadPlanEntry);
    let day: Days | undefined;
    mount(MealPlanLayout, {
      props: { mealplans: [{ date: new Date(2026, 9, 15), meals }] },
      global: {
        stubs: {
          "v-row": { template: "<div><slot /></div>" },
          "v-col": { template: "<div><slot /></div>" },
        },
      },
      slots: {
        default: (props: { day: Days }) => {
          day = props.day;
          return "";
        },
      },
    });
    expect(day!.sections.flatMap(section => section.meals)).toEqual(meals);
    expect(day!.sections.map(section => section.meals.length)).toEqual(sizes);
  });
});
