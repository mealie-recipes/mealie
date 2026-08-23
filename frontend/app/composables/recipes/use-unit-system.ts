import { useHouseholdSelf } from "~/composables/use-households";
import type { TemperatureUnit, UnitSystem } from "~/lib/api/types/user";

export type UnitSystemOption = { label: string; value: UnitSystem };
export type TemperatureUnitOption = { label: string; value: TemperatureUnit };

/**
 * Resolve how recipe quantities and temperatures should be displayed.
 *
 * Precedence is user preference, then household default, then "as written". A per-recipe
 * override is layered on top by the recipe page itself and is deliberately not persisted:
 * peeking at a recipe in metric should not change the setting everywhere else.
 */
export function useUnitSystem() {
  const auth = useMealieAuth();
  const { household } = useHouseholdSelf();
  const i18n = useI18n();

  const unitSystem = computed<UnitSystem>(() =>
    auth.user.value?.preferredUnitSystem
    ?? household.value?.preferences?.defaultUnitSystem
    ?? "original",
  );

  const temperatureUnit = computed<TemperatureUnit>(() =>
    auth.user.value?.preferredTemperatureUnit
    ?? household.value?.preferences?.defaultTemperatureUnit
    ?? "system",
  );

  const unitSystemOptions = computed<UnitSystemOption[]>(() => [
    { label: i18n.t("recipe.unit-system-original"), value: "original" },
    { label: i18n.t("recipe.unit-system-metric"), value: "metric" },
    { label: i18n.t("recipe.unit-system-imperial"), value: "imperial" },
    { label: i18n.t("recipe.unit-system-us"), value: "us" },
  ]);

  const temperatureUnitOptions = computed<TemperatureUnitOption[]>(() => [
    { label: i18n.t("recipe.temperature-unit-system"), value: "system" },
    { label: i18n.t("recipe.temperature-unit-celsius"), value: "celsius" },
    { label: i18n.t("recipe.temperature-unit-fahrenheit"), value: "fahrenheit" },
  ]);

  return { unitSystem, temperatureUnit, unitSystemOptions, temperatureUnitOptions };
}
