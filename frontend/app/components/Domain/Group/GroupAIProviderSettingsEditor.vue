<template>
  <div v-if="providerSettings">
    <BaseCardSectionTitle v-if="!hideHeader" :title="$t('group.ai-provider-settings.ai-provider-settings')">
      <template v-if="noDefaultProviderWarning" #append-title>
        <v-tooltip location="bottom" color="warning">
          <template #activator="{ props: tooltipProps }">
            <v-icon v-bind="tooltipProps" size="small" color="warning" class="ms-2">
              {{ $globals.icons.alert }}
            </v-icon>
          </template>
          <span>{{ $t('group.ai-provider-settings.no-default-provider-warning') }}</span>
        </v-tooltip>
      </template>
    </BaseCardSectionTitle>
    <v-card-text v-if="!hideHeader" class="pt-0 pb-10 px-0">
      {{ $t("group.ai-provider-settings.ai-provider-settings-description") }}
    </v-card-text>

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
        <v-card-subtitle class="mt-1">
          {{ $t("group.ai-provider-settings.default-provider-description") }}
        </v-card-subtitle>
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
        <v-card-subtitle class="mt-1">
          {{ $t("group.ai-provider-settings.audio-provider-description") }}
        </v-card-subtitle>
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
        <v-card-subtitle class="mt-1">
          {{ $t("group.ai-provider-settings.image-provider-description") }}
        </v-card-subtitle>
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
        <div class="d-flex align-center ms-auto">
          <v-switch
            v-model="autoTestPreferences.autoTest"
            :label="$t('group.ai-provider-settings.auto-test')"
            color="primary"
            density="compact"
            hide-details
            class="me-1"
          />
          <v-tooltip location="bottom">
            <template #activator="{ props: tooltipProps }">
              <v-icon v-bind="tooltipProps" size="small" class="me-4">
                {{ $globals.icons.informationOutline }}
              </v-icon>
            </template>
            <span>{{ $t('group.ai-provider-settings.auto-test-description') }}</span>
          </v-tooltip>
          <BaseButton
            :text="$t('group.ai-provider-settings.create-provider')"
            class="my-2"
            create
            small
            @click="openCreate"
          />
        </div>
      </template>
    </BaseCardSectionTitle>

    <v-card
      v-for="provider in local.providers"
      :key="provider.id"
      variant="tonal"
      class="pa-0 mb-4"
    >
      <v-row no-gutters align="center">
        <v-col :cols="6">
          <v-card-text>
            {{ provider.name }}
          </v-card-text>
        </v-col>

        <v-col :cols="6" class="d-flex align-center justify-end">
          <GroupAIProviderTestBadge
            :ref="(el) => setTestBadgeRef(provider.id, el)"
            :provider-id="provider.id"
            :auto-test="autoTestPreferences.autoTest"
            class="me-2"
            @testing-change="(testing) => setTesting(provider.id, testing)"
          />
          <BaseButtonGroup
            :buttons="[
              {
                icon: $globals.icons.refresh,
                text: $t('group.ai-provider-settings.test-connection'),
                event: 'test',
                loading: testingProviderIds.has(provider.id),
                disabled: testingProviderIds.has(provider.id),
              },
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
            @test="testBadgeRefs.get(provider.id)?.runTest()"
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
import { useAIProviderPreferences } from "~/composables/use-users/preferences";

const autoTestPreferences = useAIProviderPreferences();

const providerSettings = defineModel<AIProviderSettingsOut>({ required: true });

const props = withDefaults(defineProps<{
  hideHeader?: boolean;
}>(), {
  hideHeader: false,
});

const { hideHeader } = toRefs(props);

const local = reactive({ ...providerSettings.value });
watch(local, (newVal) => { providerSettings.value = { ...newVal }; });
// Sync back when the parent refreshes after create/update/delete
watch(providerSettings, (newVal) => { if (newVal) Object.assign(local, newVal); });

const noDefaultProviderWarning = computed(
  () => local.providers.length > 0 && !local.defaultProviderId,
);

defineEmits<{
  (e: "create", data: AIProviderCreate): void;
  (e: "update", id: string, data: AIProviderUpdate): void;
  (e: "delete", id: string): void;
}>();

const dialogOpen = ref(false);
const editingProviderId = ref<string | null>(null);

interface TestBadgeInstance {
  runTest: () => Promise<void>;
}

const testBadgeRefs = new Map<string, TestBadgeInstance>();
function setTestBadgeRef(providerId: string, el: unknown) {
  if (el) testBadgeRefs.set(providerId, el as TestBadgeInstance);
  else testBadgeRefs.delete(providerId);
}

// Tracks which rows currently have a test in flight (manual click or AutoTest-triggered) so the
// button group can show a loading state and block repeat clicks until the result comes back.
const testingProviderIds = reactive(new Set<string>());
function setTesting(providerId: string, testing: boolean) {
  if (testing) testingProviderIds.add(providerId);
  else testingProviderIds.delete(providerId);
}

function openCreate() {
  editingProviderId.value = null;
  dialogOpen.value = true;
}

function openEdit(id: string) {
  editingProviderId.value = id;
  dialogOpen.value = true;
}
</script>
