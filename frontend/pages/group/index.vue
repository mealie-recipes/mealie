<template>
  <v-container class="narrow-container">
    <BasePageTitle class="mb-5">
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/manage-group-settings.svg')"></v-img>
      </template>
      <template #title> {{ $t("profile.group-settings") }} </template>
      {{ $t("profile.group-description") }}
    </BasePageTitle>

    <section v-if="group">
      <BaseCardSectionTitle class="mt-10" :title="$tc('group.group-preferences')"></BaseCardSectionTitle>
      <div class="mb-6">
        <v-checkbox
          v-model="group.preferences.privateGroup"
          hide-details
          dense
          :label="$t('group.private-group')"
          @change="groupActions.updatePreferences()"
        />
        <div class="ml-8">
          <p class="text-subtitle-2 my-0 py-0">
            {{ $t("group.private-group-description") }}
          </p>
          <DocLink class="mt-2" link="/documentation/getting-started/faq/#how-do-private-groups-and-recipes-work" />
        </div>
      </div>
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
        {{ $t("group.default-recipe-preferences-description") }}
      </BaseCardSectionTitle>

      <div class="preference-container">
        <div v-for="p in preferencesEditor" :key="p.key">
          <v-checkbox
            v-model="group.preferences[p.key]"
            hide-details
            dense
            :label="p.label"
            @change="groupActions.updatePreferences()"
          />
          <p class="ml-8 text-subtitle-2 my-0 py-0">
            {{ p.description }}
          </p>
        </div>
      </div>
    </section>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
import { useGroupSelf } from "~/composables/use-groups";
import { ReadGroupPreferences } from "~/lib/api/types/group";

export default defineComponent({
  middleware: ["auth", "can-manage-only"],
  setup() {
    const { group, actions: groupActions } = useGroupSelf();

    const { i18n } = useContext();

    type Preference = {
      key: keyof ReadGroupPreferences;
      value: boolean;
      label: string;
      description: string;
    };

    const preferencesEditor = computed<Preference[]>(() => {
      if (!group.value || !group.value.preferences) {
        return [];
      }
      return [
        {
          key: "recipePublic",
          value: group.value.preferences.recipePublic || false,
          label: i18n.t("group.allow-users-outside-of-your-group-to-see-your-recipes"),
          description: i18n.t("group.allow-users-outside-of-your-group-to-see-your-recipes-description"),
        } as Preference,
        {
          key: "recipeShowNutrition",
          value: group.value.preferences.recipeShowNutrition || false,
          label: i18n.t("group.show-nutrition-information"),
          description: i18n.t("group.show-nutrition-information-description"),
        } as Preference,
        {
          key: "recipeShowAssets",
          value: group.value.preferences.recipeShowAssets || false,
          label: i18n.t("group.show-recipe-assets"),
          description: i18n.t("group.show-recipe-assets-description"),
        } as Preference,
        {
          key: "recipeLandscapeView",
          value: group.value.preferences.recipeLandscapeView || false,
          label: i18n.t("group.default-to-landscape-view"),
          description: i18n.t("group.default-to-landscape-view-description"),
        } as Preference,
        {
          key: "recipeDisableComments",
          value: group.value.preferences.recipeDisableComments || false,
          label: i18n.t("group.disable-users-from-commenting-on-recipes"),
          description: i18n.t("group.disable-users-from-commenting-on-recipes-description"),
        } as Preference,
        {
          key: "recipeDisableAmount",
          value: group.value.preferences.recipeDisableAmount || false,
          label: i18n.t("group.disable-organizing-recipe-ingredients-by-units-and-food"),
          description: i18n.t("group.disable-organizing-recipe-ingredients-by-units-and-food-description"),
        } as Preference,
      ];
    });

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
      preferencesEditor,
    };
  },
  head() {
    return {
      title: this.$t("group.group") as string,
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
