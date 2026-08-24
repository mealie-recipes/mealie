<template>
  <div>
    <div
      class="d-md-flex"
      style="gap: 10px"
    >
      <v-select
        v-model="day"
        :items="MEAL_DAY_OPTIONS"
        :label="$t('meal-plan.rule-day')"
      />
      <v-select
        v-model="entryType"
        :items="MEAL_TYPE_OPTIONS"
        :label="$t('meal-plan.meal-type')"
      />
    </div>

    <div class="mb-5">
      <QueryFilterBuilder
        :field-defs="fieldDefs"
        :initial-query-filter="props.queryFilter"
        @input="handleQueryFilterInput"
      />
    </div>

    <!-- TODO: proper pluralization of inputDay -->
    {{ $t('meal-plan.this-rule-will-apply', {
      dayCriteria: day === "unset" ? $t('meal-plan.to-all-days') : $t('meal-plan.on-days', [day]),
      mealTypeCriteria: entryType === "unset" ? $t('meal-plan.for-all-meal-types') : $t('meal-plan.for-type-meal-types', [entryType]),
    }) }}
  </div>
</template>

<script setup lang="ts">
import QueryFilterBuilder from "~/components/Domain/QueryFilterBuilder.vue";
import type { FieldDefinition } from "~/composables/use-query-filter-builder";
import { Organizer } from "~/lib/api/types/non-generated";
import type { QueryFilterJSON } from "~/lib/api/types/non-generated";

interface Props {
  queryFilter?: QueryFilterJSON | null;
  showHelp?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  queryFilter: null,
  showHelp: false,
});

const day = defineModel<string>("day", { default: "unset" });
const entryType = defineModel<string>("entryType", { default: "unset" });
const queryFilterString = defineModel<string>("queryFilterString", { default: "" });

const i18n = useI18n();

const MEAL_TYPE_OPTIONS = [
  { title: i18n.t("meal-plan.breakfast"), value: "breakfast" },
  { title: i18n.t("meal-plan.lunch"), value: "lunch" },
  { title: i18n.t("meal-plan.dinner"), value: "dinner" },
  { title: i18n.t("meal-plan.side"), value: "side" },
  { title: i18n.t("meal-plan.snack"), value: "snack" },
  { title: i18n.t("meal-plan.drink"), value: "drink" },
  { title: i18n.t("meal-plan.dessert"), value: "dessert" },
  { title: i18n.t("meal-plan.type-any"), value: "unset" },
];

const MEAL_DAY_OPTIONS = [
  { title: i18n.t("general.monday"), value: "monday" },
  { title: i18n.t("general.tuesday"), value: "tuesday" },
  { title: i18n.t("general.wednesday"), value: "wednesday" },
  { title: i18n.t("general.thursday"), value: "thursday" },
  { title: i18n.t("general.friday"), value: "friday" },
  { title: i18n.t("general.saturday"), value: "saturday" },
  { title: i18n.t("general.sunday"), value: "sunday" },
  { title: i18n.t("meal-plan.day-any"), value: "unset" },
];

function handleQueryFilterInput(value: string | undefined) {
  queryFilterString.value = value || "";
}

const fieldDefs: FieldDefinition[] = [
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
</script>
