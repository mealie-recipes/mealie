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

        <div v-if="testResult" class="mt-4">
          <div class="d-flex align-center">
            <v-icon :color="checkColor(textCheckState)" size="small" class="me-2">
              {{ checkIcon(textCheckState) }}
            </v-icon>
            <span class="text-body-2">{{ $t('group.ai-provider-settings.test-check-text') }}</span>
          </div>
          <div v-if="!testResult.success && testResult.message" class="text-caption text-medium-emphasis ms-7 mb-2">
            {{ testResult.message }}
          </div>

          <div class="d-flex align-center mt-1">
            <v-icon :color="checkColor(imageCheckState)" size="small" class="me-2">
              {{ checkIcon(imageCheckState) }}
            </v-icon>
            <span class="text-body-2">{{ $t('group.ai-provider-settings.test-check-image') }}</span>
          </div>
          <div v-if="imageCheckMessage" class="text-caption text-medium-emphasis ms-7">
            {{ imageCheckMessage }}
          </div>
        </div>
      </v-form>
    </v-card-text>
    <AppLoader v-else />

    <template #custom-card-action>
      <v-btn
        variant="text"
        :loading="testing"
        :disabled="submitDisabled"
        @click="handleTest"
      >
        {{ $t('group.ai-provider-settings.test-connection') }}
      </v-btn>
    </template>
  </BaseDialog>
</template>

<script setup lang="ts">
import { useAIProviders } from "~/composables/use-ai-providers";
import { validators } from "~/composables/use-validators";
import type { AIProviderCreate, AIProviderTestResult, AIProviderUpdate } from "~/lib/api/types/group";

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
const i18n = useI18n();
const { loading, getOne, testOne, testSavedOne } = useAIProviders();
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

const testing = ref(false);
const testResult = ref<AIProviderTestResult | null>(null);

// Bumped every time the dialog starts testing a (possibly different) provider, so a slow
// response that's still in flight when the user switches providers gets ignored instead of
// silently overwriting the result now being shown for someone else's config.
let testRequestId = 0;

const submitDisabled = computed(() => {
  return !formData.name?.trim() || !formData.model?.trim() || (!isEdit.value && !formData.apiKey?.trim());
});

type CheckState = "passed" | "failed" | "pending";

const textCheckState = computed<CheckState | null>(() => {
  if (!testResult.value) return null;
  return testResult.value.success ? "passed" : "failed";
});

const imageCheckState = computed<CheckState | null>(() => {
  const result = testResult.value;
  if (!result) return null;
  if (!result.success) return "pending"; // text check failed - image check never ran
  return result.imageTestPassed ? "passed" : "failed";
});

// Only shown for a failure - a passing image check needs no further explanation, and "pending"
// already reads as self-explanatory next to the failed text check above it.
const imageCheckMessage = computed(() => {
  const result = testResult.value;
  if (!result?.success || result.imageTestPassed) return "";
  return result.imageTestMessage || i18n.t("group.ai-provider-settings.test-connection-image-not-recognized");
});

function checkIcon(state: CheckState | null) {
  if (state === "passed") return $globals.icons.check;
  if (state === "failed") return $globals.icons.close;
  return $globals.icons.minus;
}

function checkColor(state: CheckState | null) {
  if (state === "passed") return "success";
  if (state === "failed") return "error";
  return undefined;
}

// Fetch existing provider when editing; reset form for create mode
watch(
  () => [dialog.value, props.providerId] as const,
  async ([open, id]) => {
    if (!open) return;
    testResult.value = null;
    testRequestId++; // invalidate any test still in flight for whatever was shown before
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
  testResult.value = null;
}

async function handleTest() {
  const requestId = ++testRequestId;
  testing.value = true;
  testResult.value = null;
  try {
    let data: AIProviderTestResult | null;
    if (isEdit.value && props.providerId) {
      // Test the form's CURRENT values, not what's saved in the DB — the user may have just
      // changed the model/base_url. If they left the API key blank (meaning "keep the existing
      // one"), the backend falls back to the saved key since we don't have that value here.
      const overrides: AIProviderUpdate & { apiKey?: string } = {
        name: formData.name,
        model: formData.model,
        baseUrl: formData.baseUrl || null,
        timeout: formData.timeout,
        requestHeaders: Object.keys(formData.requestHeaders).length ? formData.requestHeaders : undefined,
        requestParams: Object.keys(formData.requestParams).length ? formData.requestParams : undefined,
      };
      if (formData.apiKey) {
        overrides.apiKey = formData.apiKey;
      }
      ({ data } = await testSavedOne(props.providerId, overrides));
    }
    else {
      ({ data } = await testOne({
        name: formData.name,
        model: formData.model,
        apiKey: formData.apiKey,
        baseUrl: formData.baseUrl || null,
        timeout: formData.timeout,
        requestHeaders: Object.keys(formData.requestHeaders).length ? formData.requestHeaders : undefined,
        requestParams: Object.keys(formData.requestParams).length ? formData.requestParams : undefined,
      } as AIProviderCreate));
    }

    if (requestId !== testRequestId) return; // stale — dialog has moved on to another provider
    testResult.value = data;
  }
  finally {
    if (requestId === testRequestId) testing.value = false;
  }
}
</script>
