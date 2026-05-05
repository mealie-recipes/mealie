import { useHouseholdSelf } from "~/composables/use-households";
import type { UnitSystem } from "~/lib/api/types/user";

/**
 * Resolve the user's preferred unit system for recipe display.
 *
 * Precedence: per-recipe view-state (handled by the caller) → user preference
 * → household default → "original".
 */
export function useUnitSystem() {
  const auth = useMealieAuth();
  const { household } = useHouseholdSelf();

  const resolvedDefault = computed<UnitSystem>(() => {
    return auth.user.value?.preferredUnitSystem
      ?? household.value?.preferences?.defaultUnitSystem
      ?? "original";
  });

  return { resolvedDefault };
}
