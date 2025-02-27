type I18n = ReturnType<typeof useI18n>;
type TRoute = string;
type TranslationResult = string;

type ActivityRoute = (groupSlug?: string) => TRoute;
type ActivityLabel = (i18n: I18n) => TranslationResult;

type Activity = {
  key: ActivityKey;
  route: ActivityRoute;
  label: ActivityLabel;
};

export const enum ActivityKey {
  RECIPES = "recipes",
  MEALPLANNER = "mealplanner",
  SHOPPING_LIST = "shopping_list",
}

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

export function getDefaultActivityRoute(activityKey?: ActivityKey, groupSlug?: string): string {
  if (!activityKey) {
    return DEFAULT_ACTIVITY;
  }
  const route = selectableActivities[activityKey]?.route ?? (() => DEFAULT_ACTIVITY);
  return route(groupSlug);
}

export function getDefaultActivityLabels(i18n: I18n): TranslationResult[] {
  return Object.values(selectableActivities).map(
    ({ label }) => label(i18n),
  );
}

export function getActivityKey(i18n: I18n, target: TranslationResult = ""): ActivityKey | undefined {
  return Object.values(selectableActivities)
    .find(({ label }) => label(i18n) === target)?.key;
}

export function getActivityLabel(i18n: I18n, target?: ActivityKey): TranslationResult {
  return Object.values(selectableActivities)
    .find(({ key }) => key === target)
    ?.label(i18n) ?? "";
}
