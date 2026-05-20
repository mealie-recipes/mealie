<template>
  <div v-if="providerSettings">
    <BaseCardSectionTitle :title="$t('group.ai-provider-settings.ai-provider-settings')" />

    <v-row class="mb-4">
      <v-col cols="12">
        <v-autocomplete
          v-model="local.defaultProviderId"
          :label="$t('group.ai-provider-settings.default-provider')"
          :items="local.providers"
          item-title="name"
          item-value="id"
          clearable
          hide-details
          density="compact"
          variant="outlined"
        />
      </v-col>
      <v-col cols="12">
        <v-autocomplete
          v-model="local.audioProviderId"
          :label="$t('group.ai-provider-settings.audio-provider')"
          :items="local.providers"
          item-title="name"
          item-value="id"
          clearable
          hide-details
          density="compact"
          variant="outlined"
        />
      </v-col>
      <v-col cols="12">
        <v-autocomplete
          v-model="local.imageProviderId"
          :label="$t('group.ai-provider-settings.image-provider')"
          :items="local.providers"
          item-title="name"
          item-value="id"
          clearable
          hide-details
          density="compact"
          variant="outlined"
        />
      </v-col>
    </v-row>

    <GroupAIProviderDialog
      v-model="dialogOpen"
      :provider-id="editingProviderId ?? undefined"
      @create="(data) => $emit('create', data)"
      @update="(id, data) => $emit('update', id, data)"
    />

    <BaseCardSectionTitle
      :title="$t('group.ai-provider-settings.providers')"
      size="medium"
      class="pt-2"
    >
      <template #append-title>
        <BaseButton
          :text="$t('group.ai-provider-settings.create-provider')"
          class="ms-auto my-2"
          create
          small
          @click="openCreate"
        />
      </template>
    </BaseCardSectionTitle>

    <v-card
      v-for="provider in local.providers"
      :key="provider.id"
      variant="tonal"
      class="pa-0 mb-4"
    >
      <v-row no-gutters>
        <v-col :cols="10">
          <v-card-text>
            {{ provider.name }}
          </v-card-text>
        </v-col>

        <v-col :cols="2">
          <BaseButtonGroup
            :buttons="[
              {
                icon: $globals.icons.edit,
                text: $t('general.edit'),
                event: 'edit',
              },
              {
                icon: $globals.icons.delete,
                text: $t('general.delete'),
                event: 'delete',
              },
            ]"
            @edit="openEdit(provider.id)"
            @delete="$emit('delete', provider.id)"
          />
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import type { AIProviderCreate, AIProviderUpdate } from "~/lib/api/types/group";
import type { AIProviderSettingsOut } from "~/lib/api/types/user";

const providerSettings = defineModel<AIProviderSettingsOut>({ required: true });
const local = reactive({ ...providerSettings.value });
watch(local, (newVal) => { providerSettings.value = { ...newVal }; });
// Sync back when the parent refreshes after create/update/delete
watch(providerSettings, (newVal) => { if (newVal) Object.assign(local, newVal); });

defineEmits<{
  (e: "create", data: AIProviderCreate): void;
  (e: "update", id: string, data: AIProviderUpdate): void;
  (e: "delete", id: string): void;
}>();

const dialogOpen = ref(false);
const editingProviderId = ref<string | null>(null);

function openCreate() {
  editingProviderId.value = null;
  dialogOpen.value = true;
}

function openEdit(id: string) {
  editingProviderId.value = id;
  dialogOpen.value = true;
}
</script>
