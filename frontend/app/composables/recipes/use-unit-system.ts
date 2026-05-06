import { useHouseholdSelf } from "~/composables/use-households";
import type { UnitSystem } from "~/lib/api/types/user";

export type UnitSystemOption = { label: string; value: UnitSystem };

/**
 * Resolve the user's preferred unit system for recipe display.
 *
 * Precedence: per-recipe view-state (handled by the caller) → user preference
 * → household default → "original". Also exposes a translated option list
 * for the toggle and the settings selectors.
 */
export function useUnitSystem() {
  const auth = useMealieAuth();
  const { household } = useHouseholdSelf();
  const i18n = useI18n();

  const resolvedDefault = computed<UnitSystem>(() => {
    return auth.user.value?.preferredUnitSystem
      ?? household.value?.preferences?.defaultUnitSystem
      ?? "original";
  });

  const options = computed<UnitSystemOption[]>(() => [
    { label: i18n.t("recipe.unit-system-original") as string, value: "original" },
    { label: i18n.t("recipe.unit-system-metric") as string, value: "metric" },
    { label: i18n.t("recipe.unit-system-imperial") as string, value: "imperial" },
    { label: i18n.t("recipe.unit-system-us") as string, value: "us" },
  ]);

  return { resolvedDefault, options };
}
