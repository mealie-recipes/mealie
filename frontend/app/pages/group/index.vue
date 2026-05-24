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

    <div class="mb-10">
      <v-form ref="refGroupPrefsEditForm" @submit.prevent="handlePrefsSubmit">
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
    </div>

    <div>
      <v-form ref="refGroupAISettingsForm" @submit.prevent="handleAISettingsSubmit">
        <v-card variant="outlined" style="border-color: lightgray;">
          <v-card-text>
            <GroupAIProviderSettingsEditor
              v-if="group.aiProviderSettings"
              v-model="group.aiProviderSettings"
              @create="handleCreateProvider"
              @update="handleUpdateProvider"
              @delete="handleDeleteProvider"
            />
          </v-card-text>
        </v-card>
        <div class="d-flex pa-2">
          <BaseButton type="submit" edit class="ml-auto">
            {{ $t("general.update") }}
          </BaseButton>
        </div>
      </v-form>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import GroupPreferencesEditor from "~/components/Domain/Group/GroupPreferencesEditor.vue";
import GroupAIProviderSettingsEditor from "~/components/Domain/Group/GroupAIProviderSettingsEditor.vue";
import { useGroupSelf } from "~/composables/use-groups";
import { useAIProviders } from "~/composables/use-ai-providers";
import { alert } from "~/composables/use-toast";
import type { AIProviderCreate, AIProviderUpdate } from "~/lib/api/types/group";
import type { VForm } from "~/types/auto-forms";

definePageMeta({
  middleware: ["can-manage-only"],
});

const { group, actions: groupActions } = useGroupSelf();
const i18n = useI18n();

useSeoMeta({
  title: i18n.t("group.group"),
});

const refGroupPrefsEditForm = ref<VForm | null>(null);
const refGroupAISettingsForm = ref<VForm | null>(null);

async function handlePrefsSubmit() {
  if (!refGroupPrefsEditForm.value?.validate() || !group.value?.preferences) {
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

async function handleAISettingsSubmit() {
  if (!refGroupAISettingsForm.value?.validate() || !group.value?.aiProviderSettings) {
    return;
  }

  const data = await groupActions.updateAIProviderSettings();
  if (data) {
    alert.success(i18n.t("settings.settings-updated"));
  }
  else {
    alert.error(i18n.t("settings.settings-update-failed"));
  }
}

const { createOne, updateOne, deleteOne } = useAIProviders();

async function handleCreateProvider(data: AIProviderCreate) {
  const result = await createOne(data);
  if (result.data) {
    await groupActions.refresh();
    alert.success(i18n.t("group.ai-provider-settings.provider-created"));
  }
  else {
    alert.error(i18n.t("group.ai-provider-settings.provider-create-failed"));
  }
}

async function handleUpdateProvider(id: string, data: AIProviderUpdate) {
  const result = await updateOne(id, data);
  if (result.data) {
    await groupActions.refresh();
    alert.success(i18n.t("group.ai-provider-settings.provider-updated"));
  }
  else {
    alert.error(i18n.t("group.ai-provider-settings.provider-update-failed"));
  }
}

async function handleDeleteProvider(id: string) {
  const result = await deleteOne(id);
  if (result.data) {
    await groupActions.refresh();
    alert.success(i18n.t("group.ai-provider-settings.provider-deleted"));
  }
  else {
    alert.error(i18n.t("group.ai-provider-settings.provider-delete-failed"));
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
