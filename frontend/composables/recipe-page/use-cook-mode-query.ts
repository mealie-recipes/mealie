import { ref, watch, type ComputedRef, type WritableComputedRef } from "vue";
import { PageMode } from "./shared-state";

export type BooleanString = "true" | "false" | "";

interface UseCookModeQueryOptions {
  cookQuery: WritableComputedRef<BooleanString | undefined>;
  isEditMode: ComputedRef<boolean>;
  pageMode: ComputedRef<PageMode>;
  setMode: (mode: PageMode) => void;
}

export function useCookModeQuery({
  cookQuery,
  isEditMode,
  pageMode,
  setMode,
}: UseCookModeQueryOptions) {
  const hasHydrated = ref(false);

  const syncCookModeWithQuery = () => {
    if (!hasHydrated.value || isEditMode.value) {
      return;
    }

    if (cookQuery.value === "true" && pageMode.value !== PageMode.COOK) {
      setMode(PageMode.COOK);
      return;
    }

    if (cookQuery.value !== "true" && pageMode.value === PageMode.COOK) {
      setMode(PageMode.VIEW);
    }
  };

  watch([cookQuery, isEditMode], syncCookModeWithQuery);

  watch(pageMode, (mode) => {
    if (!hasHydrated.value) {
      return;
    }

    if (mode === PageMode.COOK) {
      if (cookQuery.value !== "true") {
        cookQuery.value = "true";
      }
      return;
    }

    if (mode === PageMode.VIEW) {
      cookQuery.value = undefined;
    }
  });

  function hydrateCookMode() {
    hasHydrated.value = true;
    syncCookModeWithQuery();
  }

  return {
    hydrateCookMode,
  };
}
