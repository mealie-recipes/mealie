<template>
  <v-container
    v-if="group"
    class="narrow-container"
  >
    <BasePageTitle>
      <template #header>
        <v-img
          width="100%"
          max-height="125"
          max-width="125"
          src="/svgs/manage-group-settings.svg"
        />
      </template>
      <template #title>
        {{ $t('group.admin-group-management') }}
      </template>
    </BasePageTitle>
    <AppToolbar back />
    <v-card-text> {{ $t('group.group-id-value', [group.id]) }} </v-card-text>
    <v-form
      v-if="!userError"
      ref="refGroupEditForm"
      @submit.prevent="handleSubmit"
    >
      <v-card variant="outlined" style="border-color: lightgrey;">
        <v-card-text>
          <v-text-field
            v-model="group.name"
            :label="$t('group.group-name')"
          />
          <GroupPreferencesEditor
            v-if="group.preferences"
            v-model="group.preferences"
          />
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

<script setup lang="ts">
import GroupPreferencesEditor from "~/components/Domain/Group/GroupPreferencesEditor.vue";
import GroupAIProviderSettingsEditor from "~/components/Domain/Group/GroupAIProviderSettingsEditor.vue";
import { useAdminApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import type { AIProviderCreate, AIProviderUpdate } from "~/lib/api/types/group";
import type { VForm } from "vuetify/components";

definePageMeta({
  layout: "admin",
});
const route = useRoute();

const i18n = useI18n();

const groupId = computed(() => route.params.id as string);

// ==============================================
// New User Form

const refGroupEditForm = ref<VForm | null>(null);

const adminApi = useAdminApi();

const userError = ref(false);

const { data: group, refresh } = useLazyAsyncData(`get-household-${groupId.value}`, async () => {
  if (!groupId.value) {
    return null;
  }
  const { data, error } = await adminApi.groups.getOne(groupId.value);

  if (error?.response?.status === 404) {
    alert.error(i18n.t("user.user-not-found"));
    userError.value = true;
  }
  return data;
}, { watch: [groupId] });

async function handleSubmit() {
  if (!refGroupEditForm.value?.validate() || !group.value) {
    return;
  }

  const { response, data } = await adminApi.groups.updateOne(group.value.id, group.value);
  if (response?.status === 200 && data) {
    if (group.value.slug !== data.slug) {
      // the slug updated, which invalidates the nav URLs
      window.location.reload();
    }
    group.value = data;
    alert.success(i18n.t("settings.settings-updated"));
  }
  else {
    alert.error(i18n.t("settings.settings-update-failed"));
  }
}

async function handleCreateProvider(data: AIProviderCreate) {
  if (!group.value) return;
  const result = await adminApi.aiProviders.createProvider(group.value.id, data);
  if (result.data) {
    await refresh();
    alert.success(i18n.t("group.ai-provider-settings.provider-created"));
  }
  else {
    alert.error(i18n.t("group.ai-provider-settings.provider-create-failed"));
  }
}

async function handleUpdateProvider(id: string, data: AIProviderUpdate) {
  if (!group.value) return;
  const result = await adminApi.aiProviders.updateProvider(group.value.id, id, data);
  if (result.data) {
    await refresh();
    alert.success(i18n.t("group.ai-provider-settings.provider-updated"));
  }
  else {
    alert.error(i18n.t("group.ai-provider-settings.provider-update-failed"));
  }
}

async function handleDeleteProvider(id: string) {
  if (!group.value) return;
  const result = await adminApi.aiProviders.deleteProvider(group.value.id, id);
  if (result.data) {
    await refresh();
    alert.success(i18n.t("group.ai-provider-settings.provider-deleted"));
  }
  else {
    alert.error(i18n.t("group.ai-provider-settings.provider-delete-failed"));
  }
}
</script>
