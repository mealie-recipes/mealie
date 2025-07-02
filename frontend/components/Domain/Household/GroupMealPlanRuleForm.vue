<template>
  <div>
    <div
      class="d-md-flex"
      style="gap: 10px"
    >
      <v-select
        v-model="inputDay"
        :items="MEAL_DAY_OPTIONS"
        :label="$t('meal-plan.rule-day')"
      />
      <v-select
        v-model="inputEntryType"
        :items="MEAL_TYPE_OPTIONS"
        :label="$t('meal-plan.meal-type')"
      />
    </div>

    <div class="mb-5">
      <QueryFilterBuilder
        :field-defs="fieldDefs"
        :initial-query-filter="queryFilter"
        @input="handleQueryFilterInput"
      />
    </div>

    <!-- TODO: proper pluralization of inputDay -->
    {{ $t('meal-plan.this-rule-will-apply', {
      dayCriteria: inputDay === "unset" ? $t('meal-plan.to-all-days') : $t('meal-plan.on-days', [inputDay]),
      mealTypeCriteria: inputEntryType === "unset" ? $t('meal-plan.for-all-meal-types') : $t('meal-plan.for-type-meal-types', [inputEntryType]),
    }) }}
  </div>
</template>

<script lang="ts">
import QueryFilterBuilder from "~/components/Domain/QueryFilterBuilder.vue";
import type { FieldDefinition } from "~/composables/use-query-filter-builder";
import { Organizer } from "~/lib/api/types/non-generated";
import type { QueryFilterJSON } from "~/lib/api/types/response";

export default defineNuxtComponent({
  components: {
    QueryFilterBuilder,
  },
  props: {
    day: {
      type: String,
      default: "unset",
    },
    entryType: {
      type: String,
      default: "unset",
    },
    queryFilterString: {
      type: String,
      default: "",
    },
    queryFilter: {
      type: Object as () => QueryFilterJSON,
      default: null,
    },
    showHelp: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["update:day", "update:entry-type", "update:query-filter-string"],
  setup(props, context) {
    const i18n = useI18n();

    const MEAL_TYPE_OPTIONS = [
      { title: i18n.t("meal-plan.breakfast"), value: "breakfast" },
      { title: i18n.t("meal-plan.lunch"), value: "lunch" },
      { title: i18n.t("meal-plan.dinner"), value: "dinner" },
      { title: i18n.t("meal-plan.side"), value: "side" },
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

    const inputDay = computed({
      get: () => {
        return props.day;
      },
      set: (val) => {
        context.emit("update:day", val);
      },
    });

    const inputEntryType = computed({
      get: () => {
        return props.entryType;
      },
      set: (val) => {
        context.emit("update:entry-type", val);
      },
    });

    const inputQueryFilterString = computed({
      get: () => {
        return props.queryFilterString;
      },
      set: (val) => {
        context.emit("update:query-filter-string", val);
      },
    });

    function handleQueryFilterInput(value: string | undefined) {
      inputQueryFilterString.value = value || "";
    };

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
        name: "last_made",
        label: i18n.t("general.last-made"),
        type: "date",
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

    return {
      MEAL_TYPE_OPTIONS,
      MEAL_DAY_OPTIONS,
      inputDay,
      inputEntryType,
      inputQueryFilterString,
      handleQueryFilterInput,
      fieldDefs,
    };
  },
});
</script>
