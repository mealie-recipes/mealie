<template>
  <v-container
    v-if="household"
    class="narrow-container"
  >
    <BasePageTitle>
      <template #header>
        <v-img
          width="100%"
          max-height="125"
          max-width="125"
          :src="require('~/static/svgs/manage-group-settings.svg')"
        />
      </template>
      <template #title>
        {{ $t('household.admin-household-management') }}
      </template>
      {{ $t('household.admin-household-management-text') }}
    </BasePageTitle>
    <AppToolbar back />
    <v-card-text> {{ $t('household.household-id-value', [household.id]) }} </v-card-text>
    <v-form
      v-if="!userError"
      ref="refHouseholdEditForm"
      @submit.prevent="handleSubmit"
    >
      <v-card variant="outlined" style="border-color: lightgrey;">
        <v-card-text>
          <v-select
            v-if="groups"
            v-model="household.groupId"
            disabled
            :items="groups"
            variant="solo-filled"
            flat
            item-title="name"
            item-value="id"
            :return-object="false"
            :label="$t('group.user-group')"
            :rules="[validators.required]"
          />
          <v-text-field
            v-model="household.name"
            variant="solo-filled"
            flat
            :label="$t('household.household-name')"
            :rules="[validators.required]"
          />
          <HouseholdPreferencesEditor
            v-if="household.preferences"
            v-model="household.preferences"
            variant="solo-filled"
            flat
          />
        </v-card-text>
      </v-card>
      <div class="d-flex pa-2">
        <BaseButton
          type="submit"
          edit
          class="ml-auto"
        >
          {{ $t("general.update") }}
        </BaseButton>
      </div>
    </v-form>
  </v-container>
</template>

<script lang="ts">
import HouseholdPreferencesEditor from "~/components/Domain/Household/HouseholdPreferencesEditor.vue";
import { useGroups } from "~/composables/use-groups";
import { useAdminApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { validators } from "~/composables/use-validators";

export default defineNuxtComponent({
  components: {
    HouseholdPreferencesEditor,
  },
  setup() {
    definePageMeta({
      layout: "admin",
    });

    const route = useRoute();
    const i18n = useI18n();

    const { groups } = useGroups();
    const householdId = computed(() => route.params.id as string);

    // ==============================================
    // New User Form

    const refHouseholdEditForm = ref<VForm | null>(null);

    const adminApi = useAdminApi();

    const userError = ref(false);

    const { data: household } = useAsyncData(`get-household-${householdId.value}`, async () => {
      if (!householdId.value) {
        return null;
      }
      const { data, error } = await adminApi.households.getOne(householdId.value);

      if (error?.response?.status === 404) {
        alert.error(i18n.t("user.user-not-found"));
        userError.value = true;
      }
      return data;
    }, { watch: [householdId] });

    async function handleSubmit() {
      if (!refHouseholdEditForm.value?.validate() || household.value === null) {
        return;
      }

      const { response, data } = await adminApi.households.updateOne(household.value.id, household.value);
      if (response?.status === 200 && data) {
        household.value = data;
        alert.success(i18n.t("settings.settings-updated"));
      }
      else {
        alert.error(i18n.t("settings.settings-update-failed"));
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
