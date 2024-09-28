<template>
  <v-container v-if="household" class="narrow-container">
    <BasePageTitle class="mb-5">
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/manage-group-settings.svg')"></v-img>
      </template>
      <template #title> {{ $t("profile.household-settings") }} </template>
      {{ $t("profile.household-description") }}
    </BasePageTitle>
    <v-form ref="refHouseholdEditForm" @submit.prevent="handleSubmit">
      <v-card outlined>
        <v-card-text>
          <HouseholdPreferencesEditor v-if="household.preferences" v-model="household.preferences" />
        </v-card-text>
      </v-card>
      <div class="d-flex pa-2">
        <BaseButton type="submit" edit class="ml-auto"> {{ $t("general.update") }}</BaseButton>
      </div>
    </v-form>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useContext } from "@nuxtjs/composition-api";
import HouseholdPreferencesEditor from "~/components/Domain/Household/HouseholdPreferencesEditor.vue";
import { VForm } from "~/types/vuetify";
import { useHouseholdSelf } from "~/composables/use-households";
import { ReadHouseholdPreferences } from "~/lib/api/types/household";
import { alert } from "~/composables/use-toast";

export default defineComponent({
  components: {
    HouseholdPreferencesEditor,
  },
  middleware: ["auth", "can-manage-household-only"],
  setup() {
    const { household, actions: householdActions } = useHouseholdSelf();
    const { i18n } = useContext();

    const refHouseholdEditForm = ref<VForm | null>(null);

    type Preference = {
      key: keyof ReadHouseholdPreferences;
      value: boolean;
      label: string;
      description: string;
    };

    const preferencesEditor = computed<Preference[]>(() => {
      if (!household.value || !household.value.preferences) {
        return [];
      }
      return [
        {
          key: "recipePublic",
          value: household.value.preferences.recipePublic || false,
          label: i18n.t("household.allow-users-outside-of-your-household-to-see-your-recipes"),
          description: i18n.t("household.allow-users-outside-of-your-household-to-see-your-recipes-description"),
        } as Preference,
        {
          key: "recipeShowNutrition",
          value: household.value.preferences.recipeShowNutrition || false,
          label: i18n.t("group.show-nutrition-information"),
          description: i18n.t("group.show-nutrition-information-description"),
        } as Preference,
        {
          key: "recipeShowAssets",
          value: household.value.preferences.recipeShowAssets || false,
          label: i18n.t("group.show-recipe-assets"),
          description: i18n.t("group.show-recipe-assets-description"),
        } as Preference,
        {
          key: "recipeLandscapeView",
          value: household.value.preferences.recipeLandscapeView || false,
          label: i18n.t("group.default-to-landscape-view"),
          description: i18n.t("group.default-to-landscape-view-description"),
        } as Preference,
        {
          key: "recipeDisableComments",
          value: household.value.preferences.recipeDisableComments || false,
          label: i18n.t("group.disable-users-from-commenting-on-recipes"),
          description: i18n.t("group.disable-users-from-commenting-on-recipes-description"),
        } as Preference,
        {
          key: "recipeDisableAmount",
          value: household.value.preferences.recipeDisableAmount || false,
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

    async function handleSubmit() {
      if (!refHouseholdEditForm.value?.validate() || !household.value?.preferences) {
        console.log(refHouseholdEditForm.value?.validate());
        return;
      }

      const data = await householdActions.updatePreferences();
      if (data) {
        alert.success(i18n.tc("settings.settings-updated"));
      } else {
        alert.error(i18n.tc("settings.settings-update-failed"));
      }
    }

    return {
      household,
      householdActions,
      allDays,
      preferencesEditor,
      refHouseholdEditForm,
      handleSubmit,
    };
  },
  head() {
    return {
      title: this.$t("household.household") as string,
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
