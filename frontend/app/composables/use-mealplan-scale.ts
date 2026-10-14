import type { ReadPlanEntry, UpdatePlanEntry } from "~/lib/api/types/meal-plan";

export const MEALPLAN_SCALE_SAVE_DELAY_MS = 400;

/**
 * Editable copy of a meal plan entry's recipe scale.
 *
 * Changes are saved through `save` once the scale has been left alone for `delay` ms, so stepping
 * through several values results in a single request.
 */
export function useMealPlanScale(
  meal: MaybeRefOrGetter<ReadPlanEntry>,
  save: (payload: UpdatePlanEntry) => unknown,
  delay = MEALPLAN_SCALE_SAVE_DELAY_MS,
) {
  const savedScale = computed(() => toValue(meal).recipeScale ?? 1);
  const scale = ref(savedScale.value);

  // RecipeSummary has no fallback of its own, so a recipe without servings is treated as serving one
  const recipeServings = computed(() => {
    const recipe = toValue(meal).recipe;
    return recipe?.recipeServings || recipe?.recipeYieldQuantity || 1;
  });

  let saveTimer: ReturnType<typeof setTimeout> | null = null;

  function saveNow() {
    saveTimer = null;
    if (scale.value !== savedScale.value) {
      save({ ...toValue(meal), recipeScale: scale.value });
    }
  }

  /** Saves a pending change immediately instead of waiting out the delay. */
  function flush() {
    if (saveTimer) {
      clearTimeout(saveTimer);
      saveNow();
    }
  }

  watch(scale, () => {
    if (saveTimer) {
      clearTimeout(saveTimer);
      saveTimer = null;
    }
    if (scale.value !== savedScale.value) {
      saveTimer = setTimeout(saveNow, delay);
    }
  }, { flush: "sync" });

  watch(savedScale, (newScale) => {
    // an entry refreshed while an edit is still waiting to be saved would otherwise undo that edit
    if (!saveTimer) {
      scale.value = newScale;
    }
  }, { flush: "sync" });

  // don't lose an edit when the control goes away before the delay has passed (e.g. navigating away)
  if (getCurrentScope()) {
    onScopeDispose(flush);
  }

  return {
    scale,
    recipeServings,
    flush,
  };
}
