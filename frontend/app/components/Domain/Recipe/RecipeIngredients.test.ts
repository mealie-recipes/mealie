import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { nextTick } from "vue";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import RecipeIngredients from "./RecipeIngredients.vue";
import type { RecipeIngredient } from "~/lib/api/types/recipe";
import { useLocales } from "~/composables/use-locales";

vi.mock("~/composables/use-locales");

const ingredients = {
  curryPaste: {
    referenceId: "ingredient-curry-paste",
    quantity: 1,
    food: { id: "food-1", name: "curry paste" },
  },
  coconutMilk: {
    referenceId: "ingredient-coconut-milk",
    quantity: 1,
    food: { id: "food-2", name: "coconut milk" },
  },
} satisfies Record<string, RecipeIngredient>;

function mountIngredients(value: RecipeIngredient[], storageKey = "recipe-ingredients:test-recipe:checked") {
  return mount(RecipeIngredients, {
    props: {
      value,
      storageKey,
    },
    global: {
      stubs: {
        AppButtonCopy: true,
        RecipeIngredientListItem: true,
        VCheckbox: {
          props: ["modelValue"],
          emits: ["update:modelValue"],
          template: `
            <button
              class="checkbox"
              type="button"
              :aria-pressed="modelValue ? 'true' : 'false'"
              @click="$emit('update:modelValue', !modelValue)"
            />
          `,
        },
        VDivider: true,
        VListItem: {
          template: "<div class=\"list-item\" @click=\"$emit('click', $event)\"><slot name=\"prepend\" /><slot /></div>",
        },
        VListItemTitle: {
          template: "<div><slot /></div>",
        },
      },
    },
  });
}

describe("RecipeIngredients", () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.mocked(useLocales).mockReturnValue({
      locales: [{ value: "en-US", pluralFoodHandling: "always" }],
      locale: { value: "en-US", pluralFoodHandling: "always" },
    } as any);
  });

  test("restores checked ingredients from session storage by reference id", async () => {
    const firstWrapper = mountIngredients([ingredients.curryPaste, ingredients.coconutMilk]);
    await firstWrapper.findAll(".checkbox")[0].trigger("click");
    await nextTick();

    expect(firstWrapper.findAll(".checkbox")[0].attributes("aria-pressed")).toBe("true");
    firstWrapper.unmount();

    const secondWrapper = mountIngredients([ingredients.coconutMilk, ingredients.curryPaste]);

    expect(secondWrapper.findAll(".checkbox")[0].attributes("aria-pressed")).toBe("false");
    expect(secondWrapper.findAll(".checkbox")[1].attributes("aria-pressed")).toBe("true");
  });

  test("gives each ingredient checkbox the ingredient text as its accessible name", () => {
    const wrapper = mount(RecipeIngredients, {
      props: {
        value: [
          { quantity: 1, unit: { id: "unit-1", name: "cup", pluralName: "cups" }, food: { id: "food-3", name: "flour" } },
          { quantity: 0, note: "salt to taste" },
        ],
        scale: 2,
      },
      global: {
        plugins: [createVuetify({ components, directives })],
        stubs: { AppButtonCopy: true, RecipeIngredientListItem: true },
      },
    });

    const labels = wrapper.findAll("input[type='checkbox']").map(input => input.attributes("aria-label"));
    expect(labels).toEqual(["2 cups flour", "salt to taste"]);
  });
});
