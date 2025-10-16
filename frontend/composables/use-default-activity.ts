import type { Activity, I18n, TranslationResult } from "~/lib/api/types/activity";
import { ActivityKey } from "~/lib/api/types/activity";

export const DEFAULT_ACTIVITY = "/g/home" as const;

type ActivityRegistry = {
  recipes: Activity;
  mealplanner: Activity;
  shopping_list: Activity;
};

const selectableActivities: ActivityRegistry = {
  recipes: {
    key: ActivityKey.RECIPES,
    route: groupSlug => groupSlug ? `/g/${groupSlug}` : DEFAULT_ACTIVITY,
    label: i18n => i18n.t("general.recipes"),
  },
  mealplanner: {
    key: ActivityKey.MEALPLANNER,
    route: () => "/household/mealplan/planner/view",
    label: i18n => i18n.t("meal-plan.meal-planner"),
  },
  shopping_list: {
    key: ActivityKey.SHOPPING_LIST,
    route: () => "/shopping-lists",
    label: i18n => i18n.t("shopping-list.shopping-lists"),
  },
};

function getDefaultActivityRoute(activityKey?: ActivityKey, groupSlug?: string): string {
  if (!activityKey) {
    return DEFAULT_ACTIVITY;
  }
  const route = selectableActivities[activityKey]?.route ?? (() => DEFAULT_ACTIVITY);
  return route(groupSlug);
}

function getDefaultActivityLabels(i18n: I18n): TranslationResult[] {
  return Object.values(selectableActivities).map(
    ({ label }) => label(i18n),
  );
}

function getActivityKey(i18n: I18n, target: TranslationResult = ""): ActivityKey | undefined {
  return Object.values(selectableActivities)
    .find(({ label }) => label(i18n) === target)?.key;
}

function getActivityLabel(i18n: I18n, target?: ActivityKey): TranslationResult {
  return Object.values(selectableActivities)
    .find(({ key }) => key === target)
    ?.label(i18n) ?? "";
}

export default function useDefaultActivity() {
  return {
    selectableActivities,
    getDefaultActivityRoute,
    getDefaultActivityLabels,
    getActivityKey,
    getActivityLabel,
  };
}
