<template>
  <v-container v-if="household" class="narrow-container">
    <BasePageTitle>
      <template #header>
        <v-img max-height="125" max-width="125" :src="require('~/static/svgs/manage-group-settings.svg')"></v-img>
      </template>
      <template #title> {{ $t('household.admin-household-management') }} </template>
      {{ $t('household.admin-household-management-text') }}
    </BasePageTitle>
    <AppToolbar back> </AppToolbar>
    <v-card-text> {{ $t('household.household-id-value', [household.id]) }} </v-card-text>
    <v-form v-if="!userError" ref="refHouseholdEditForm" @submit.prevent="handleSubmit">
      <v-card outlined>
        <v-card-text>
          <v-select
            v-if="groups"
            v-model="household.groupId"
            disabled
            :items="groups"
            rounded
            class="rounded-lg"
            item-text="name"
            item-value="id"
            :return-object="false"
            filled
            :label="$tc('group.user-group')"
            :rules="[validators.required]"
          />
          <v-text-field
            v-model="household.name"
            :label="$t('household.household-name')"
            :rules="[validators.required]"
          />
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
import { defineComponent, useRoute, onMounted, ref, useContext } from "@nuxtjs/composition-api";
import HouseholdPreferencesEditor from "~/components/Domain/Household/HouseholdPreferencesEditor.vue";
import { useGroups } from "~/composables/use-groups";
import { useAdminApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { validators } from "~/composables/use-validators";
import { HouseholdInDB } from "~/lib/api/types/household";
import { VForm } from "~/types/vuetify";

export default defineComponent({
  components: {
    HouseholdPreferencesEditor,
  },
  layout: "admin",
  setup() {
    const route = useRoute();
    const { i18n } = useContext();

    const { groups } = useGroups();
    const householdId = route.value.params.id;

    // ==============================================
    // New User Form

    const refHouseholdEditForm = ref<VForm | null>(null);

    const adminApi = useAdminApi();

    const household = ref<HouseholdInDB | null>(null);

    const userError = ref(false);

    onMounted(async () => {
      const { data, error } = await adminApi.households.getOne(householdId);

      if (error?.response?.status === 404) {
        alert.error(i18n.tc("user.user-not-found"));
        userError.value = true;
      }

      if (data) {
          household.value = data;
      }
    });

    async function handleSubmit() {
      if (!refHouseholdEditForm.value?.validate() || household.value === null) {
        return;
      }

      const { response, data } = await adminApi.households.updateOne(household.value.id, household.value);
      if (response?.status === 200 && data) {
        household.value = data;
        alert.success(i18n.tc("settings.settings-updated"));
      } else {
        alert.error(i18n.tc("settings.settings-update-failed"));
      }
    }

    return {
      groups,
      household,
      validators,
      userError,
      refHouseholdEditForm,
      handleSubmit,
    };
  },
});
</script>
