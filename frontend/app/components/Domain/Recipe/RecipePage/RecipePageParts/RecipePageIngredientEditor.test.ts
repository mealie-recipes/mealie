import { mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { nextTick, ref } from "vue";
import RecipePageIngredientEditor from "./RecipePageIngredientEditor.vue";
import type { Recipe } from "~/lib/api/types/recipe";

vi.mock("~/composables/recipe-page/shared-state", () => ({
  usePageState: () => ({
    toggleIsParsing: vi.fn(),
  }),
}));

const wrappers: VueWrapper[] = [];

function mountEditor(recipe = ref<Recipe>({
  id: "recipe-1",
  slug: "test-recipe",
  name: "Test Recipe",
  recipeIngredient: [
    { referenceId: "ref-1", quantity: 1, note: "first ingredient" },
    { referenceId: "ref-2", quantity: 2, note: "second ingredient" },
  ],
})) {
  const wrapper = mount(RecipePageIngredientEditor, {
    props: {
      "modelValue": recipe.value,
      "onUpdate:modelValue": (val: Recipe) => {
        recipe.value = val;
      },
    },
    global: {
      mocks: {
        $globals: {
          icons: {
            information: "info",
            foods: "foods",
            createAlt: "createAlt",
            chevronDown: "chevronDown",
            silverwareForkKnife: "forkKnife",
            create: "create",
          },
        },
      },
      stubs: {
        VueDraggable: {
          props: ["modelValue"],
          template: "<div><slot /></div>",
        },
        RecipeIngredientEditor: {
          props: ["modelValue"],
          emits: ["ctrl-enter", "insert-above", "insert-below", "delete"],
          template: `
            <div class="ingredient-row" :data-reference-id="modelValue.referenceId">
              <input class="quantity-input" :value="modelValue.quantity" />
              <button class="trigger-ctrl-enter" @click="$emit('ctrl-enter')">Ctrl+Enter</button>
              <button class="trigger-delete" @click="$emit('delete')">Delete</button>
            </div>
          `,
        },
        RecipeDialogBulkAdd: true,
        BaseButton: true,
        VAlert: true,
        VBtn: true,
        VIcon: true,
        VMenu: true,
        VList: true,
        VListItem: true,
        VSkeletonLoader: true,
      },
    },
    attachTo: document.body,
  });

  wrappers.push(wrapper);
  return { wrapper, recipe };
}

describe("RecipePageIngredientEditor", () => {
  beforeEach(() => {
    vi.stubGlobal("useNuxtApp", () => ({
      $globals: {
        icons: {
          information: "info",
          foods: "foods",
          createAlt: "createAlt",
          chevronDown: "chevronDown",
          silverwareForkKnife: "forkKnife",
          create: "create",
        },
      },
    }));
  });

  afterEach(() => {
    wrappers.forEach(wrapper => wrapper.unmount());
    wrappers.length = 0;
    vi.unstubAllGlobals();
  });

  test("ctrl-enter on first ingredient inserts a new ingredient row at index 1 and focuses its quantity input", async () => {
    const { wrapper, recipe } = mountEditor();

    const firstRowButton = wrapper.findAll(".trigger-ctrl-enter")[0];
    await firstRowButton.trigger("click");
    await nextTick();

    expect(recipe.value.recipeIngredient).toHaveLength(3);
    expect(recipe.value.recipeIngredient[0].referenceId).toBe("ref-1");
    expect(recipe.value.recipeIngredient[2].referenceId).toBe("ref-2");

    const insertedIngredient = recipe.value.recipeIngredient[1];
    expect(insertedIngredient.quantity).toBe(0);
    expect(insertedIngredient.referenceId).toBeTruthy();

    await nextTick();
    const newRow = document.querySelector(`[data-reference-id="${insertedIngredient.referenceId}"]`);
    const input = newRow?.querySelector("input");
    expect(document.activeElement).toBe(input);
  });

  test("delete event removes the corresponding ingredient from the recipe", async () => {
    const { wrapper, recipe } = mountEditor();

    const firstRowDeleteButton = wrapper.findAll(".trigger-delete")[0];
    await firstRowDeleteButton.trigger("click");
    await nextTick();

    expect(recipe.value.recipeIngredient).toHaveLength(1);
    expect(recipe.value.recipeIngredient[0].referenceId).toBe("ref-2");
  });
});
