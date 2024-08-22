<template>
  <div v-if="preferences">
    <BaseCardSectionTitle :title="$tc('group.general-preferences')"></BaseCardSectionTitle>
    <v-checkbox v-model="preferences.privateHousehold" class="mt-n4" :label="$t('household.private-household')"></v-checkbox>
    <v-select
      v-model="preferences.firstDayOfWeek"
      :prepend-icon="$globals.icons.calendarWeekBegin"
      :items="allDays"
      item-text="name"
      item-value="value"
      :label="$t('settings.first-day-of-week')"
    />

    <BaseCardSectionTitle class="mt-5" :title="$tc('household.household-recipe-preferences')"></BaseCardSectionTitle>
    <template v-for="(_, key) in preferences">
      <v-checkbox
        v-if="labels[key]"
        :key="key"
        v-model="preferences[key]"
        class="mt-n4"
        :label="labels[key]"
      ></v-checkbox>
    </template>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, useContext } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    value: {
      type: Object,
      required: true,
    },
  },
  setup(props, context) {
    const { i18n } = useContext();

    const labels = {
      recipePublic: i18n.tc("household.allow-users-outside-of-your-household-to-see-your-recipes"),
      recipeShowNutrition: i18n.tc("group.show-nutrition-information"),
      recipeShowAssets: i18n.tc("group.show-recipe-assets"),
      recipeLandscapeView: i18n.tc("group.default-to-landscape-view"),
      recipeDisableComments: i18n.tc("group.disable-users-from-commenting-on-recipes"),
      recipeDisableAmount: i18n.tc("group.disable-organizing-recipe-ingredients-by-units-and-food"),
    };

    const allDays = [
      {
        name: i18n.t("general.sunday"),
        value: 0,
      },
      {
        name: i18n.t("general.monday"),
        value: 1,
      },
      {
        name: i18n.t("general.tuesday"),
        value: 2,
      },
      {
        name: i18n.t("general.wednesday"),
        value: 3,
      },
      {
        name: i18n.t("general.thursday"),
        value: 4,
      },
      {
        name: i18n.t("general.friday"),
        value: 5,
      },
      {
        name: i18n.t("general.saturday"),
        value: 6,
      },
    ];

    const preferences = computed({
      get() {
        return props.value;
      },
      set(val) {
        context.emit("input", val);
      },
    });

    return {
      allDays,
      labels,
      preferences,
    };
  },
});
</script>

<style lang="scss" scoped>
</style>
