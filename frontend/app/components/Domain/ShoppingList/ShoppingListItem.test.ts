import { describe, test, expect, vi, beforeEach, afterEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import ShoppingListItem from "./ShoppingListItem.vue";
import { useLocales } from "~/composables/use-locales";
import type { ShoppingListItemOut } from "~/lib/api/types/household";

vi.mock("~/composables/use-locales");

const vuetify = createVuetify({ components, directives });

describe("ShoppingListItem", () => {
  beforeEach(() => {
    vi.stubGlobal("useRtl", () => ({ isRtl: ref(false) }));
    vi.mocked(useLocales).mockReturnValue({
      locales: [{ value: "en-US", pluralFoodHandling: "always" }],
      locale: { value: "en-US", pluralFoodHandling: "always" },
    } as any);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("gives the item checkbox the item text as its accessible name", () => {
    const item = {
      id: "item-1",
      shoppingListId: "list-1",
      checked: false,
      position: 0,
      quantity: 3,
      unit: null,
      food: { id: "food-1", name: "apple", pluralName: "apples" },
      note: "",
      display: "3 apples",
      recipeReferences: [],
    } as unknown as ShoppingListItemOut;

    const wrapper = mount(ShoppingListItem, {
      props: { modelValue: item, labels: [], units: [], foods: [] },
      global: {
        plugins: [vuetify],
        mocks: { $globals: { icons: new Proxy({}, { get: (_, name) => String(name) }) } },
        stubs: { RecipeIngredientListItem: true, ShoppingListItemEditor: true, RecipeList: true },
      },
    });

    expect(wrapper.find("input[type='checkbox']").attributes("aria-label")).toBe("3 apples");
  });
});
