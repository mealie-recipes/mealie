<template>
  <div>
    <div class="d-md-flex" style="gap: 10px">
      <v-select v-model="inputDay" :items="MEAL_DAY_OPTIONS" :label="$t('meal-plan.rule-day')"></v-select>
      <v-select v-model="inputEntryType" :items="MEAL_TYPE_OPTIONS" :label="$t('meal-plan.meal-type')"></v-select>
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
         mealTypeCriteria: inputEntryType === "unset" ? $t('meal-plan.for-all-meal-types') : $t('meal-plan.for-type-meal-types', [inputEntryType])
        }) }}
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, useContext } from "@nuxtjs/composition-api";
import QueryFilterBuilder from "~/components/Domain/QueryFilterBuilder.vue";
import { FieldDefinition } from "~/composables/use-query-filter-builder";
import { Organizer } from "~/lib/api/types/non-generated";
import { QueryFilterJSON } from "~/lib/api/types/response";

export default defineComponent({
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
  setup(props, context) {
    const { i18n } = useContext();

    const MEAL_TYPE_OPTIONS = [
      { text: i18n.t("meal-plan.breakfast"), value: "breakfast" },
      { text: i18n.t("meal-plan.lunch"), value: "lunch" },
      { text: i18n.t("meal-plan.dinner"), value: "dinner" },
      { text: i18n.t("meal-plan.side"), value: "side" },
      { text: i18n.t("meal-plan.type-any"), value: "unset" },
    ];

    const MEAL_DAY_OPTIONS = [
      { text: i18n.t("general.monday"), value: "monday" },
      { text: i18n.t("general.tuesday"), value: "tuesday" },
      { text: i18n.t("general.wednesday"), value: "wednesday" },
      { text: i18n.t("general.thursday"), value: "thursday" },
      { text: i18n.t("general.friday"), value: "friday" },
      { text: i18n.t("general.saturday"), value: "saturday" },
      { text: i18n.t("general.sunday"), value: "sunday" },
      { text: i18n.t("meal-plan.day-any"), value: "unset" },
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
        label: i18n.tc("category.categories"),
        type: Organizer.Category,
      },
      {
        name: "tags.id",
        label: i18n.tc("tag.tags"),
        type: Organizer.Tag,
      },
      {
        name: "recipe_ingredient.food.id",
        label: i18n.tc("recipe.ingredients"),
        type: Organizer.Food,
      },
      {
        name: "tools.id",
        label: i18n.tc("tool.tools"),
        type: Organizer.Tool,
      },
      {
        name: "household_id",
        label: i18n.tc("household.households"),
        type: Organizer.Household,
      },
      {
        name: "last_made",
        label: i18n.tc("general.last-made"),
        type: "date",
      },
      {
        name: "created_at",
        label: i18n.tc("general.date-created"),
        type: "date",
      },
      {
        name: "updated_at",
        label: i18n.tc("general.date-updated"),
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
