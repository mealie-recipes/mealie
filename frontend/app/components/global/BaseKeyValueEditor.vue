<template>
  <div>
    <div
      v-for="(value, key) in (modelValue ?? {})"
      :key="key"
      class="d-flex align-center mb-2 gap-2"
    >
      <v-text-field
        :model-value="key"
        :label="resolvedKeyLabel"
        density="compact"
        variant="outlined"
        hide-details
        readonly
        class="me-3 flex-grow-1"
      />
      <v-text-field
        :model-value="value"
        :label="resolvedValueLabel"
        density="compact"
        variant="outlined"
        hide-details
        class="ms-3 flex-grow-1"
        @update:model-value="updateValue(key, $event)"
      />
      <v-btn
        icon
        variant="text"
        color="error"
        size="small"
        @click="removeEntry(key)"
      >
        <v-icon>{{ $globals.icons.delete }}</v-icon>
      </v-btn>
    </div>

    <div class="d-flex align-center mt-2 gap-2" @focusout="onNewEntryFocusOut">
      <v-text-field
        v-model="newKey"
        :label="resolvedKeyLabel"
        density="compact"
        variant="outlined"
        hide-details
        class="me-3 flex-grow-1"
        @keydown.enter.prevent="addEntry"
      />
      <v-text-field
        v-model="newValue"
        :label="resolvedValueLabel"
        density="compact"
        variant="outlined"
        hide-details
        class="ms-3 flex-grow-1"
        @keydown.enter.prevent="addEntry"
      />
      <v-btn
        icon
        variant="text"
        color="primary"
        size="small"
        :disabled="!newKey?.trim()"
        @click="addEntry"
      >
        <v-icon>{{ $globals.icons.createAlt }}</v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useGlobalI18n } from "~/composables/use-global-i18n";

const i18n = useGlobalI18n();

const props = defineProps<{
  modelValue?: Record<string, string> | null;
  keyLabel?: string;
  valueLabel?: string;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: Record<string, string>): void;
}>();

const { $globals } = useNuxtApp();

const resolvedKeyLabel = computed(() => props.keyLabel ?? i18n.t("general.key"));
const resolvedValueLabel = computed(() => props.valueLabel ?? i18n.t("general.value"));

const newKey = ref("");
const newValue = ref("");

function current(): Record<string, string> {
  return { ...(props.modelValue ?? {}) };
}

function addEntry() {
  const key = newKey.value?.trim();
  if (!key) return;
  const updated = current();
  updated[key] = newValue.value;
  emit("update:modelValue", updated);
  newKey.value = "";
  newValue.value = "";
}

function onNewEntryFocusOut(e: FocusEvent) {
  const relatedTarget = e.relatedTarget as HTMLElement | null;
  const currentTarget = e.currentTarget as HTMLElement;
  if (!relatedTarget || !currentTarget.contains(relatedTarget)) {
    addEntry();
  }
}

function updateValue(key: string, value: string) {
  const updated = current();
  updated[key] = value;
  emit("update:modelValue", updated);
}

function removeEntry(key: string) {
  const updated = current();
  // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
  delete updated[key];
  emit("update:modelValue", updated);
}
</script>
