<template>
  <BaseDialog
    v-model="dialog"
    :title="isEdit ? $t('group.ai-provider-settings.edit-provider') : $t('group.ai-provider-settings.create-provider')"
    :icon="$globals.icons.robot"
    :loading="loading"
    can-submit
    :submit-icon="isEdit ? $globals.icons.save : $globals.icons.createAlt"
    :submit-text="isEdit ? $t('general.update') : $t('general.create')"
    :submit-disabled="submitDisabled"
    @submit="handleSubmit"
    @close="resetForm"
  >
    <v-card-text v-if="init" style="max-height: 70vh; overflow-y: auto;">
      <v-form ref="form" v-no-autofill>
        <v-text-field
          v-model="formData.name"
          :label="$t('group.ai-provider-settings.provider-name')"
          :rules="[validators.required]"
          density="compact"
          variant="outlined"
          class="mb-4"
        />
        <v-text-field
          v-model="formData.model"
          :label="$t('group.ai-provider-settings.model')"
          :hint="$t('group.ai-provider-settings.model-description')"
          :rules="[validators.required]"
          density="compact"
          variant="outlined"
          class="mb-4"
        />
        <v-text-field
          v-model="formData.apiKey"
          :label="$t('group.ai-provider-settings.api-key')"
          :hint="$t(
            isEdit
              ? 'group.ai-provider-settings.api-key-description-edit'
              : 'group.ai-provider-settings.api-key-description-create',
          )"
          :persistent-hint="isEdit"
          :rules="isEdit ? [] : [validators.required]"
          density="compact"
          variant="outlined"
          type="password"
          class="mb-4"
        />
        <v-text-field
          v-model="formData.baseUrl"
          :label="$t('group.ai-provider-settings.base-url')"
          :hint="$t('group.ai-provider-settings.base-url-description')"
          density="compact"
          variant="outlined"
          class="mb-4"
        />
        <v-number-input
          v-model.number="formData.timeout"
          :label="$t('group.ai-provider-settings.request-timeout-seconds')"
          type="number"
          :min="0"
          hide-details
          control-variant="stacked"
          density="compact"
          variant="outlined"
          class="mb-4"
        />
        <v-expansion-panels v-model="advancedPanel" variant="accordion">
          <v-expansion-panel>
            <v-expansion-panel-title class="text-subtitle-2" expand-icon="$expand" collapse-icon="$expand">
              {{ $t('search.advanced') }}
            </v-expansion-panel-title>
            <v-expansion-panel-text class="px-0">
              <div class="mb-2 text-subtitle-2">
                {{ $t('group.ai-provider-settings.request-headers') }}
              </div>
              <BaseKeyValueEditor
                v-model="formData.requestHeaders"
                class="mb-4"
              />
              <v-divider class="mb-4" />
              <div class="mb-2 text-subtitle-2">
                {{ $t('group.ai-provider-settings.request-params') }}
              </div>
              <BaseKeyValueEditor
                v-model="formData.requestParams"
              />
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-form>
    </v-card-text>
    <AppLoader v-else waiting-text="" />
  </BaseDialog>
</template>

<script setup lang="ts">
import { useAIProviders } from "~/composables/use-ai-providers";
import { validators } from "~/composables/use-validators";
import type { AIProviderCreate, AIProviderUpdate } from "~/lib/api/types/group";

const props = withDefaults(defineProps<{
  providerId?: string;
}>(), {
  providerId: undefined,
});

const emit = defineEmits<{
  (e: "create", data: AIProviderCreate): void;
  (e: "update", id: string, data: AIProviderUpdate): void;
}>();

const dialog = defineModel<boolean>({ default: false });

const { $globals } = useNuxtApp();
const { loading, getOne } = useAIProviders();
const init = ref(false);

const form = ref();
const advancedPanel = ref<number | undefined>(undefined);

const isEdit = computed(() => !!props.providerId);

const defaultForm = () => ({
  name: "",
  model: "",
  apiKey: "",
  baseUrl: "",
  timeout: 300,
  requestHeaders: {} as Record<string, string>,
  requestParams: {} as Record<string, string>,
});

const formData = reactive(defaultForm());

const submitDisabled = computed(() => {
  return !formData.name?.trim() || !formData.model?.trim() || (!isEdit.value && !formData.apiKey?.trim());
});

// Fetch existing provider when editing; reset form for create mode
watch(
  () => [dialog.value, props.providerId] as const,
  async ([open, id]) => {
    if (!open) return;
    if (!id) {
      // Create mode — just show the empty form
      resetForm();
      init.value = true;
      return;
    }
    init.value = false;
    const { data } = await getOne(id);
    init.value = true;
    if (data) {
      formData.name = data.name;
      formData.model = data.model;
      formData.apiKey = "";
      formData.baseUrl = data.baseUrl ?? "";
      formData.timeout = data.timeout ?? 300;
      formData.requestHeaders = { ...(data.requestHeaders ?? {}) };
      formData.requestParams = { ...(data.requestParams ?? {}) };
    }
  },
  { immediate: true },
);

function handleSubmit() {
  // Required field guard (button is also disabled, but keep as a safeguard)
  if (!formData.name?.trim() || !formData.model?.trim()) return;
  if (!isEdit.value && !formData.apiKey?.trim()) return;

  if (isEdit.value && props.providerId) {
    const payload: AIProviderUpdate & { apiKey?: string } = {
      name: formData.name,
      model: formData.model,
      baseUrl: formData.baseUrl || null,
      timeout: formData.timeout,
      requestHeaders: Object.keys(formData.requestHeaders).length ? formData.requestHeaders : undefined,
      requestParams: Object.keys(formData.requestParams).length ? formData.requestParams : undefined,
    };
    if (formData.apiKey) {
      payload.apiKey = formData.apiKey;
    }
    emit("update", props.providerId, payload);
  }
  else {
    const createPayload = {
      name: formData.name,
      model: formData.model,
      apiKey: formData.apiKey,
      baseUrl: formData.baseUrl || null,
      timeout: formData.timeout,
      requestHeaders: Object.keys(formData.requestHeaders).length ? formData.requestHeaders : undefined,
      requestParams: Object.keys(formData.requestParams).length ? formData.requestParams : undefined,
    };
    emit("create", createPayload as AIProviderCreate);
  }
}

function resetForm() {
  Object.assign(formData, defaultForm());
  form.value?.reset();
  advancedPanel.value = undefined;
}
</script>
