import { useUserApi } from "~/composables/api";
import type { PlanEntryType, PlanRulesDay, PlanRulesOut } from "~/lib/api/types/meal-plan";

const DAYS_OF_WEEK: PlanRulesDay[] = [
  "sunday",
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
];

export function getDayOfWeek(date: Date): PlanRulesDay {
  return DAYS_OF_WEEK[date.getDay()] ?? "unset";
}

export function getApplicableRules(
  rules: PlanRulesOut[],
  date: Date,
  entryType: PlanEntryType,
): PlanRulesOut[] {
  const day = getDayOfWeek(date);

  return rules.filter((rule) => {
    const dayMatches = !rule.day || rule.day === "unset" || rule.day === day;
    const typeMatches = !rule.entryType || rule.entryType === "unset" || rule.entryType === entryType;
    return dayMatches && typeMatches;
  });
}

export function buildRuleQueryFilter(
  rules: PlanRulesOut[],
  date: Date,
  entryType: PlanEntryType,
): string | null {
  const queryFilters = getApplicableRules(rules, date, entryType)
    .map(rule => rule.queryFilterString)
    .filter(queryFilterString => !!queryFilterString)
    .map(queryFilterString => `(${queryFilterString})`);

  return queryFilters.length ? queryFilters.join(" AND ") : null;
}

const rules = ref<PlanRulesOut[]>([]);
const loading = ref(false);
const initialized = ref(false);

export function resetMealplanRuleStore() {
  rules.value = [];
  loading.value = false;
  initialized.value = false;
}

export const useMealplanRules = function () {
  const api = useUserApi();

  async function refresh() {
    loading.value = true;

    const { data } = await api.mealplanRules.getAll();
    if (data) {
      rules.value = data.items ?? [];
    }

    initialized.value = true;
    loading.value = false;
  }

  // initial hydration
  if (!loading.value && !initialized.value) {
    refresh();
  }

  return { rules, loading, initialized, refresh };
};
