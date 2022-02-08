<template>
  <v-container class="narrow-container">
    <BasePageTitle class="mb-5">
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/manage-group-settings.svg')"></v-img>
      </template>
      <template #title> Group Settings </template>
      These items are shared within your group. Editing one of them will change it for the whole group!
    </BasePageTitle>

    <section v-if="group">
      <BaseCardSectionTitle class="mt-10" title="Group Preferences"></BaseCardSectionTitle>
      <v-checkbox
        v-model="group.preferences.privateGroup"
        class="mt-n4"
        label="Private Group"
        @change="groupActions.updatePreferences()"
      ></v-checkbox>
      <v-select
        v-model="group.preferences.firstDayOfWeek"
        :prepend-icon="$globals.icons.calendarWeekBegin"
        :items="allDays"
        item-text="name"
        item-value="value"
        :label="$t('settings.first-day-of-week')"
        @change="groupActions.updatePreferences()"
      />
    </section>

    <section v-if="group">
      <BaseCardSectionTitle class="mt-10" title="Default Recipe Preferences">
        These are the default settings when a new recipe is created in your group. These can be changed for indivdual
        recipes in the recipe settings menu.
      </BaseCardSectionTitle>

      <v-checkbox
        v-model="group.preferences.recipePublic"
        class="mt-n4"
        label="Allow users outside of your group to see your recipes"
        @change="groupActions.updatePreferences()"
      ></v-checkbox>
      <v-checkbox
        v-model="group.preferences.recipeShowNutrition"
        class="mt-n4"
        label="Show nutrition information"
        @change="groupActions.updatePreferences()"
      ></v-checkbox>
      <v-checkbox
        v-model="group.preferences.recipeShowAssets"
        class="mt-n4"
        label="Show recipe assets"
        @change="groupActions.updatePreferences()"
      ></v-checkbox>
      <v-checkbox
        v-model="group.preferences.recipeLandscapeView"
        class="mt-n4"
        label="Default to landscape view"
        @change="groupActions.updatePreferences()"
      ></v-checkbox>
      <v-checkbox
        v-model="group.preferences.recipeDisableComments"
        class="mt-n4"
        label="Allow recipe comments from users in your group"
        @change="groupActions.updatePreferences()"
      ></v-checkbox>
      <v-checkbox
        v-model="group.preferences.recipeDisableAmount"
        class="mt-n4"
        label="Enable organizing recipe ingredients by units and food"
        @change="groupActions.updatePreferences()"
      ></v-checkbox>
    </section>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, useContext } from "@nuxtjs/composition-api";
import { useGroupSelf } from "~/composables/use-groups";

export default defineComponent({
  setup() {
    const { group, actions: groupActions } = useGroupSelf();

    const { i18n } = useContext();

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

    return {
      group,
      groupActions,
      allDays,
    };
  },
  head() {
    return {
      title: this.$t("group.group") as string,
    };
  },
});
</script>
