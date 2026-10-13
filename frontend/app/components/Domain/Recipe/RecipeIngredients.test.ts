import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { nextTick } from "vue";
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
        VDivider: true,
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
    await firstWrapper.findAll(".ingredient-row__check")[0].trigger("click");
    await nextTick();

    expect(firstWrapper.findAll(".ingredient-row__check")[0].attributes("aria-checked")).toBe("true");
    firstWrapper.unmount();

    const secondWrapper = mountIngredients([ingredients.coconutMilk, ingredients.curryPaste]);

    expect(secondWrapper.findAll(".ingredient-row__check")[0].attributes("aria-checked")).toBe("false");
    expect(secondWrapper.findAll(".ingredient-row__check")[1].attributes("aria-checked")).toBe("true");
  });

  test("toggles an ingredient when its row is clicked", async () => {
    const wrapper = mountIngredients([ingredients.curryPaste], "recipe-ingredients:row-click:checked");
    await wrapper.find(".ingredient-row").trigger("click");
    await nextTick();

    expect(wrapper.find(".ingredient-row").classes()).toContain("ingredient-row--checked");
    expect(wrapper.find(".ingredient-row__check").attributes("aria-checked")).toBe("true");
  });
});
