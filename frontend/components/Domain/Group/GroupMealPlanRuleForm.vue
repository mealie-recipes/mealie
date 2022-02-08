<template>
  <div>
    <div class="d-md-flex" style="gap: 10px">
      <v-select v-model="inputDay" :items="MEAL_DAY_OPTIONS" label="Rule Day"></v-select>
      <v-select v-model="inputEntryType" :items="MEAL_TYPE_OPTIONS" label="Meal Type"></v-select>
    </div>

    <RecipeCategoryTagSelector v-model="inputCategories" />

    {{ inputDay === "unset" ? "This rule will apply to all days" : `This rule applies on ${inputDay}s` }}
    {{ inputEntryType === "unset" ? "for all meal types" : ` and for ${inputEntryType} meal types` }}
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from "@nuxtjs/composition-api";
import RecipeCategoryTagSelector from "~/components/Domain/Recipe/RecipeCategoryTagSelector.vue";

const MEAL_TYPE_OPTIONS = [
  { text: "Breakfast", value: "breakfast" },
  { text: "Lunch", value: "lunch" },
  { text: "Dinner", value: "dinner" },
  { text: "Snack", value: "snack" },
  { text: "Any", value: "unset" },
];

const MEAL_DAY_OPTIONS = [
  { text: "Monday", value: "monday" },
  { text: "Tuesday", value: "tuesday" },
  { text: "Wednesday", value: "wednesday" },
  { text: "Thursday", value: "thursday" },
  { text: "Friday", value: "friday" },
  { text: "Sunday", value: "saturday" },
  { text: "Sunday", value: "sunday" },
  { text: "Any", value: "unset" },
];

export default defineComponent({
  components: {
    RecipeCategoryTagSelector,
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
    categories: {
      type: Array,
      default: () => [],
    },
    showHelp: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, context) {
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

    const inputCategories = computed({
      get: () => {
        return props.categories;
      },
      set: (val) => {
        context.emit("update:categories", val);
      },
    });

    return {
      MEAL_TYPE_OPTIONS,
      MEAL_DAY_OPTIONS,
      inputDay,
      inputEntryType,
      inputCategories,
    };
  },
});
</script>
