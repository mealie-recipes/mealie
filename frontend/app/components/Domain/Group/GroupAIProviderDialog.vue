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
          :hint="$t(apiKeyHint)"
          :persistent-hint="isEdit"
          :rules="apiKeyRequired ? [validators.required] : []"
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
          density="compact"
          variant="outlined"
          class="mb-4"
        />
        <v-alert
          v-if="hiddenValuesNeedReentry"
          type="warning"
          density="compact"
          variant="tonal"
          class="mb-4"
        >
          {{ $t('group.ai-provider-settings.reenter-hidden-values') }}
        </v-alert>
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

        <v-alert
          v-if="testResult"
          :type="testResult.success ? 'success' : 'error'"
          density="compact"
          variant="tonal"
          class="mt-4"
        >
          {{ connectionMessage }}{{ imageSupportMessage }}
        </v-alert>
      </v-form>
    </v-card-text>
    <AppLoader v-else />

    <template #custom-card-action>
      <v-btn
        variant="text"
        :loading="testing"
        :disabled="submitDisabled || testing"
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

// The API returns this in place of stored header and param values (REDACTED_VALUE in
// mealie/schema/group/ai_providers.py). Sending it back means "keep the stored value".
const REDACTED_VALUE = "********";

// Stored secrets are bound to the base URL they were saved with, so the backend only reuses
// them while the URL is unchanged. A new URL needs a new API key and every hidden value retyped.
const savedBaseUrl = ref<string | null>(null);
const baseUrlChanged = computed(() => isEdit.value && (formData.baseUrl || null) !== savedBaseUrl.value);
const apiKeyRequired = computed(() => !isEdit.value || baseUrlChanged.value);
const hiddenValuesNeedReentry = computed(() => baseUrlChanged.value && [
  ...Object.values(formData.requestHeaders),
  ...Object.values(formData.requestParams),
].includes(REDACTED_VALUE));

const apiKeyHint = computed(() => {
  if (!isEdit.value) return "group.ai-provider-settings.api-key-description-create";
  if (baseUrlChanged.value) return "group.ai-provider-settings.api-key-description-base-url-changed";
  return "group.ai-provider-settings.api-key-description-edit";
});

watch(hiddenValuesNeedReentry, (needsReentry) => {
  if (needsReentry) advancedPanel.value = 0;
});

const testing = ref(false);
const testResult = ref<AIProviderTestResult | null>(null);

const submitDisabled = computed(() => {
  return !formData.name?.trim()
    || !formData.model?.trim()
    || (apiKeyRequired.value && !formData.apiKey?.trim())
    || hiddenValuesNeedReentry.value;
});

const connectionMessage = computed(() => {
  const result = testResult.value;
  if (!result) return "";
  if (result.success) return i18n.t("group.ai-provider-settings.test-connection-succeeded");
  return result.message || i18n.t("group.ai-provider-settings.test-connection-failed");
});

// Capability info rather than a second pass/fail check - a text-only provider is a valid setup,
// it just can't be used as the image provider. Appended to the connection message above.
// supportsImages is null when image support wasn't checked (e.g. an audio-only provider that was
// tested by transcription), so there's nothing to say about images then.
const imageSupportMessage = computed(() => {
  const result = testResult.value;
  if (!result?.success || typeof result.supportsImages !== "boolean") return "";
  return result.supportsImages
    ? ` — ${i18n.t("group.ai-provider-settings.supports-images")}`
    : ` — ${i18n.t("group.ai-provider-settings.text-only-provider")}`;
});

// Fetch existing provider when editing; reset form for create mode
let requestToken = 0;

watch(
  () => [dialog.value, props.providerId] as const,
  async ([open, id]) => {
    // Bump the token even when bailing out below, so a fetch still in flight from a
    // previous provider/dialog state can never apply its (now stale) result afterward.
    const token = ++requestToken;
    if (!open) return;
    testResult.value = null;
    if (!id) {
      // Create mode — just show the empty form
      resetForm();
      init.value = true;
      return;
    }
    init.value = false;
    const { data } = await getOne(id);
    if (token !== requestToken) return;
    init.value = true;
    if (data) {
      formData.name = data.name;
      formData.model = data.model;
      formData.apiKey = "";
      formData.baseUrl = data.baseUrl ?? "";
      savedBaseUrl.value = data.baseUrl || null;
      formData.timeout = data.timeout ?? 300;
      formData.requestHeaders = { ...(data.requestHeaders ?? {}) };
      formData.requestParams = { ...(data.requestParams ?? {}) };
    }
  },
  { immediate: true },
);

function handleSubmit() {
  // The button is also disabled; this guards submit-on-enter.
  if (submitDisabled.value) return;

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
  savedBaseUrl.value = null;
  form.value?.reset();
  advancedPanel.value = undefined;
  testResult.value = null;
}

async function handleTest() {
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

    testResult.value = data;
  }
  finally {
    testing.value = false;
  }
}
</script>
