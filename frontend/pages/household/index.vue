<template>
  <v-container
    v-if="household"
    class="narrow-container"
  >
    <BasePageTitle class="mb-5">
      <template #header>
        <v-img
          width="100%"
          max-height="100"
          max-width="100"
          src="/svgs/manage-group-settings.svg"
        />
      </template>
      <template #title>
        {{ $t("profile.household-settings") }}
      </template>
      {{ $t("profile.household-description") }}
    </BasePageTitle>
    <v-form ref="refHouseholdEditForm" @submit.prevent="handleSubmit">
      <v-card variant="outlined" style="border-color: lightgray;">
        <v-card-text>
          <HouseholdPreferencesEditor v-if="household.preferences" v-model="household.preferences" />
        </v-card-text>
      </v-card>
      <div class="d-flex pa-2">
        <BaseButton type="submit" edit class="ml-auto">
          {{ $t("general.update") }}
        </BaseButton>
      </div>
    </v-form>
  </v-container>
</template>

<script setup lang="ts">
import HouseholdPreferencesEditor from "~/components/Domain/Household/HouseholdPreferencesEditor.vue";
import { useHouseholdSelf } from "~/composables/use-households";
import { alert } from "~/composables/use-toast";
import type { VForm } from "~/types/auto-forms";

definePageMeta({
  middleware: ["can-manage-household-only"],
});

const { household, actions: householdActions } = useHouseholdSelf();
const i18n = useI18n();

useSeoMeta({
  title: i18n.t("household.household"),
});

const refHouseholdEditForm = ref<VForm | null>(null);

async function handleSubmit() {
  if (!refHouseholdEditForm.value?.validate() || !household.value?.preferences) {
    console.log(refHouseholdEditForm.value?.validate());
    return;
  }

  const data = await householdActions.updatePreferences();
  if (data) {
    alert.success(i18n.t("settings.settings-updated"));
  }
  else {
    alert.error(i18n.t("settings.settings-update-failed"));
  }
}
</script>

<style lang="css">
.preference-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 600px;
}
</style>
