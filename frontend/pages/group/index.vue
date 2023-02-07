<template>
  <v-container class="narrow-container">
    <BasePageTitle class="mb-5">
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/manage-group-settings.svg')"></v-img>
      </template>
      <template #title> {{ $t('profile.group-settings') }} </template>
      {{ $t('profile.group-description') }}
    </BasePageTitle>

    <section v-if="group">
      <BaseCardSectionTitle class="mt-10" :title="$tc('group.group-preferences')"></BaseCardSectionTitle>
      <v-checkbox
        v-model="group.preferences.privateGroup"
        class="mt-n4"
        :label="$t('group.private-group')"
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
      <BaseCardSectionTitle class="mt-10" :title="$tc('group.default-recipe-preferences')">
        {{ $t('group.default-recipe-preferences-description') }}
      </BaseCardSectionTitle>

      <v-checkbox
        v-model="group.preferences.recipePublic"
        class="mt-n4"
        :label="$t('group.allow-users-outside-of-your-group-to-see-your-recipes')"
        @change="groupActions.updatePreferences()"
      ></v-checkbox>
      <v-checkbox
        v-model="group.preferences.recipeShowNutrition"
        class="mt-n4"
        :label="$t('group.show-nutrition-information')"
        @change="groupActions.updatePreferences()"
      ></v-checkbox>
      <v-checkbox
        v-model="group.preferences.recipeShowAssets"
        class="mt-n4"
        :label="$t('group.show-recipe-assets')"
        @change="groupActions.updatePreferences()"
      ></v-checkbox>
      <v-checkbox
        v-model="group.preferences.recipeLandscapeView"
        class="mt-n4"
        :label="$t('group.default-to-landscape-view')"
        @change="groupActions.updatePreferences()"
      ></v-checkbox>
      <v-checkbox
        v-model="group.preferences.recipeDisableComments"
        class="mt-n4"
        :label="$t('group.disable-users-from-commenting-on-recipes')"
        @change="groupActions.updatePreferences()"
      ></v-checkbox>
      <v-checkbox
        v-model="group.preferences.recipeDisableAmount"
        class="mt-n4"
        :label="$t('group.disable-organizing-recipe-ingredients-by-units-and-food')"
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
