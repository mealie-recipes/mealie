<template>
  <v-number-input
    v-if="isEditMode"
    :model-value="inputMinutes"
    class="step-duration"
    :min="0"
    :max="35791394"
    :precision="0"
    :hint="modelValue && modelValue % 60 ? $t('recipe.step-duration-saved', { duration: formattedDuration }) : undefined"
    persistent-hint
    :label="$t('recipe.step-duration-minutes')"
    :placeholder="$t('recipe.step-duration-placeholder')"
    density="compact"
    inset
    hide-details="auto"
    @update:model-value="updateDuration"
    @keypress="e => e.key === '-' && e.preventDefault()"
    @click.stop
  />
  <span v-else-if="modelValue" class="text-body-2">
    {{ formattedDuration }}
  </span>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps<{
  modelValue?: number | null;
  isEditMode: boolean;
}>();
const emit = defineEmits<{ "update:modelValue": [value: number | null] }>();
const { t } = useI18n();
// Display whole minutes only; keep imported seconds untouched until the minutes change.
// The hint exposes any remainder before the user deliberately replaces it.
const inputMinutes = ref<number | null>(null);

function toSeconds(minutes: number | null) {
  return (minutes ?? 0) * 60 || null;
}

watch(
  () => props.modelValue,
  (value) => {
    // Only re-sync outside changes, so stepping down to 0 (saved as no duration) keeps showing 0
    if ((value ?? null) === toSeconds(inputMinutes.value)) return;
    inputMinutes.value = value ? Math.floor(value / 60) : null;
  },
  { immediate: true },
);

function updateDuration(value: number | null) {
  if (value === inputMinutes.value) return;
  inputMinutes.value = value;
  emit("update:modelValue", toSeconds(value));
}

const formattedDuration = computed(() => {
  const seconds = props.modelValue ?? 0;
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainder = seconds % 60;
  return [
    hours ? t("recipe.step-duration-value-hours", { hours }) : "",
    minutes ? t("recipe.step-duration-value-minutes", { minutes }) : "",
    remainder ? t("recipe.step-duration-value-seconds", { seconds: remainder }) : "",
  ].filter(Boolean).join(" ");
});
</script>

<style scoped>
/* Override the instruction title's larger input text only for this field. */
.step-duration.v-text-field :deep(input) {
  font-size: 1rem;
}
</style>
