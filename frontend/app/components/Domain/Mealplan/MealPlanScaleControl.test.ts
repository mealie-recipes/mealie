import { mount } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { defineComponent } from "vue";
import MealPlanScaleControl from "./MealPlanScaleControl.vue";
import { MEALPLAN_SCALE_SAVE_DELAY_MS } from "~/composables/use-mealplan-scale";
import type { ReadPlanEntry } from "~/lib/api/types/meal-plan";

// the real button needs vuetify; all this control adds on top of it is the debounced save
const RecipeScaleEditButton = defineComponent({
  name: "RecipeScaleEditButton",
  props: {
    modelValue: { type: Number, required: true },
    recipeServings: { type: Number, required: true },
    editScale: Boolean,
  },
  emits: ["update:modelValue"],
  template: "<div />",
});

const meal: ReadPlanEntry = {
  id: 1,
  date: "2026-08-19",
  entryType: "dinner",
  groupId: "my-group-id",
  userId: "my-user-id",
  householdId: "my-household-id",
  recipeId: "my-recipe-id",
  recipeScale: 1.5,
  recipe: { id: "my-recipe-id", name: "Pancakes", recipeServings: 4 },
};

function mountControl() {
  const actions = { updateOne: vi.fn() };
  const wrapper = mount(MealPlanScaleControl, {
    props: { meal, actions: actions as any },
    global: { stubs: { RecipeScaleEditButton } },
  });

  return { wrapper, actions, button: wrapper.findComponent(RecipeScaleEditButton) };
}

describe("MealPlanScaleControl", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  test("shows the entry's scale against the recipe's servings", () => {
    const { button } = mountControl();

    expect(button.props()).toMatchObject({ modelValue: 1.5, recipeServings: 4, editScale: true });
  });

  test("updates the entry once the scale has settled", async () => {
    const { button, actions } = mountControl();

    await button.vm.$emit("update:modelValue", 1.75);
    await button.vm.$emit("update:modelValue", 2);
    expect(button.props("modelValue")).toBe(2);
    expect(actions.updateOne).not.toHaveBeenCalled();

    vi.advanceTimersByTime(MEALPLAN_SCALE_SAVE_DELAY_MS);
    expect(actions.updateOne).toHaveBeenCalledExactlyOnceWith({ ...meal, recipeScale: 2 });
  });

  test("picks up a scale that was changed elsewhere", async () => {
    const { wrapper, button, actions } = mountControl();

    await wrapper.setProps({ meal: { ...meal, recipeScale: 3 } });
    expect(button.props("modelValue")).toBe(3);

    vi.runAllTimers();
    expect(actions.updateOne).not.toHaveBeenCalled();
  });

  test("doesn't drop a pending change when it's unmounted", async () => {
    const { wrapper, button, actions } = mountControl();

    await button.vm.$emit("update:modelValue", 2);
    wrapper.unmount();

    expect(actions.updateOne).toHaveBeenCalledExactlyOnceWith({ ...meal, recipeScale: 2 });
  });
});
