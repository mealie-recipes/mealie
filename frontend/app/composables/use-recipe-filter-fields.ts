import { Organizer } from "~/lib/api/types/non-generated";
import type { FieldDefinition } from "~/composables/use-query-filter-builder";

/**
 * Names of all recipe fields that can be used in a recipe query filter.
 */
export type RecipeFilterFieldName
  = | "recipe_category.id"
    | "tags.id"
    | "recipe_ingredient.food.id"
    | "recipe_ingredient.food.label_id"
    | "tools.id"
    | "household_id"
    | "user_id"
    | "rating"
    | "total_time_seconds"
    | "last_made"
    | "created_at"
    | "updated_at";

export interface RecipeFilterFieldOptions {
  /**
   * Fields to leave out in this context.
   *
   * Only exclude a field when the surrounding page already covers it in a way
   * that would conflict with a second filter for the same thing.
   */
  exclude?: RecipeFilterFieldName[];
}

/**
 * The single list of recipe fields offered by the query filter builder.
 *
 * Cookbooks, meal plan rules and the recipe finder all filter recipes, so they
 * share this list. A new filterable field only needs to be added here to show
 * up everywhere.
 */
export function useRecipeFilterFields(options: RecipeFilterFieldOptions = {}): FieldDefinition[] {
  const i18n = useI18n();
  const excluded = new Set(options.exclude ?? []);

  const fields: (FieldDefinition & { name: RecipeFilterFieldName })[] = [
    {
      name: "recipe_category.id",
      label: i18n.t("category.categories"),
      type: Organizer.Category,
    },
    {
      name: "tags.id",
      label: i18n.t("tag.tags"),
      type: Organizer.Tag,
    },
    {
      name: "recipe_ingredient.food.id",
      label: i18n.t("recipe.ingredients"),
      type: Organizer.Food,
    },
    {
      name: "recipe_ingredient.food.label_id",
      label: i18n.t("data-pages.foods.food-label"),
      type: Organizer.Label,
    },
    {
      name: "tools.id",
      label: i18n.t("tool.tools"),
      type: Organizer.Tool,
    },
    {
      name: "household_id",
      label: i18n.t("household.households"),
      type: Organizer.Household,
    },
    {
      name: "user_id",
      label: i18n.t("user.users"),
      type: Organizer.User,
    },
    {
      name: "rating",
      label: i18n.t("general.rating"),
      type: "number",
    },
    {
      name: "total_time_seconds",
      label: i18n.t("recipe.total-time"),
      type: "duration",
    },
    {
      name: "last_made",
      label: i18n.t("general.last-made"),
      type: "relativeDate",
    },
    {
      name: "created_at",
      label: i18n.t("general.date-created"),
      type: "date",
    },
    {
      name: "updated_at",
      label: i18n.t("general.date-updated"),
      type: "date",
    },
  ];

  return fields.filter(field => !excluded.has(field.name));
}
