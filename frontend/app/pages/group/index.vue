<template>
  <v-container
    v-if="group"
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
        {{ $t("profile.group-settings") }}
      </template>
      {{ $t("profile.group-description") }}
    </BasePageTitle>
    <v-form ref="refGroupEditForm" @submit.prevent="handleSubmit">
      <v-card variant="outlined" style="border-color: lightgray;">
        <v-card-text>
          <GroupPreferencesEditor v-if="group.preferences" v-model="group.preferences" />
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
import GroupPreferencesEditor from "~/components/Domain/Group/GroupPreferencesEditor.vue";
import { useGroupSelf } from "~/composables/use-groups";
import { alert } from "~/composables/use-toast";
import type { VForm } from "~/types/auto-forms";

definePageMeta({
  middleware: ["can-manage-only"],
});

const { group, actions: groupActions } = useGroupSelf();
const i18n = useI18n();

useSeoMeta({
  title: i18n.t("group.group"),
});

const refGroupEditForm = ref<VForm | null>(null);

async function handleSubmit() {
  if (!refGroupEditForm.value?.validate() || !group.value?.preferences) {
    return;
  }

  const data = await groupActions.updatePreferences();
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
