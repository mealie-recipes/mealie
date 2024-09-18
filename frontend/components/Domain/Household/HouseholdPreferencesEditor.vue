<template>
  <div v-if="preferences">
    <BaseCardSectionTitle class="mt-10" :title="$tc('household.household-preferences')"></BaseCardSectionTitle>
    <div class="mb-6">
      <v-checkbox
        v-model="preferences.privateHousehold"
        hide-details
        dense
        :label="$t('household.private-household')"
      />
      <div class="ml-8">
        <p class="text-subtitle-2 my-0 py-0">
          {{ $t("household.private-household-description") }}
        </p>
        <DocLink class="mt-2" link="/documentation/getting-started/faq/#how-do-private-groups-and-recipes-work" />
      </div>
    </div>
    <div class="mb-6">
      <v-checkbox
        v-model="preferences.lockRecipeEditsFromOtherHouseholds"
        hide-details
        dense
        :label="$t('household.lock-recipe-edits-from-other-households')"
      />
      <div class="ml-8">
        <p class="text-subtitle-2 my-0 py-0">
          {{ $t("household.lock-recipe-edits-from-other-households-description") }}
        </p>
      </div>
    </div>
    <v-select
      v-model="preferences.firstDayOfWeek"
      :prepend-icon="$globals.icons.calendarWeekBegin"
      :items="allDays"
      item-text="name"
      item-value="value"
      :label="$t('settings.first-day-of-week')"
    />

    <BaseCardSectionTitle class="mt-5" :title="$tc('household.household-recipe-preferences')"></BaseCardSectionTitle>
    <div class="preference-container">
      <div v-for="p in recipePreferences" :key="p.key">
        <v-checkbox
          v-model="preferences[p.key]"
          hide-details
          dense
          :label="p.label"
        />
        <p class="ml-8 text-subtitle-2 my-0 py-0">
          {{ p.description }}
        </p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, useContext } from "@nuxtjs/composition-api";
import { ReadHouseholdPreferences } from "~/lib/api/types/household";

export default defineComponent({
  props: {
    value: {
      type: Object,
      required: true,
    },
  },
  setup(props, context) {
    const { i18n } = useContext();

    type Preference = {
      key: keyof ReadHouseholdPreferences;
      label: string;
      description: string;
    }

    const recipePreferences: Preference[] = [
      {
        key: "recipePublic",
        label: i18n.tc("group.allow-users-outside-of-your-group-to-see-your-recipes"),
        description: i18n.tc("group.allow-users-outside-of-your-group-to-see-your-recipes-description"),
      },
      {
        key: "recipeShowNutrition",
        label: i18n.tc("group.show-nutrition-information"),
        description: i18n.tc("group.show-nutrition-information-description"),
      },
      {
        key: "recipeShowAssets",
        label: i18n.tc("group.show-recipe-assets"),
        description: i18n.tc("group.show-recipe-assets-description"),
      },
      {
        key: "recipeLandscapeView",
        label: i18n.tc("group.default-to-landscape-view"),
        description: i18n.tc("group.default-to-landscape-view-description"),
      },
      {
        key: "recipeDisableComments",
        label: i18n.tc("group.disable-users-from-commenting-on-recipes"),
        description: i18n.tc("group.disable-users-from-commenting-on-recipes-description"),
      },
      {
        key: "recipeDisableAmount",
        label: i18n.tc("group.disable-organizing-recipe-ingredients-by-units-and-food"),
        description: i18n.tc("group.disable-organizing-recipe-ingredients-by-units-and-food-description"),
      },
    ];

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
      preferences,
      recipePreferences,
    };
  },
});
</script>

<style lang="css">
.preference-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 600px;
}
</style>
