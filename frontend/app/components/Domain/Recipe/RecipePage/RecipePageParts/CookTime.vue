<template>
  <v-text-field
    v-if="isEditMode"
    v-model="input"
    type="number"
    min="0"
    :max="2147483647 / 60"
    step="any"
    :label="$t('recipe.step-duration-minutes')"
    :placeholder="$t('recipe.step-duration-placeholder')"
    :rules="[validDuration]"
    density="compact"
    hide-details="auto"
    @input="updateDuration"
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
const input = ref<string | number>(props.modelValue ? props.modelValue / 60 : "");
watch(() => props.modelValue, value => input.value = value ? value / 60 : "");

const badInput = ref(false);

function secondsFromMinutes(value: string | number | null) {
  const original = props.modelValue;
  // Division and multiplication need not round-trip at large magnitudes.
  // Preserve the exact stored integer when the displayed minutes are unchanged.
  if (typeof original === "number" && Number.isInteger(original)
    && original > 0 && original <= 2147483647 && Number(value) === original / 60) {
    return original;
  }
  return Number(value) * 60;
}

function validDuration(value: string | number | null) {
  if (badInput.value) return t("recipe.step-duration-invalid");
  if (value === "" || value === null) return true;
  const seconds = secondsFromMinutes(value);
  // Permit floating-point representation noise, never a fractional second.
  return (Number.isFinite(seconds) && seconds >= 0 && seconds <= 2147483647
    && Math.abs(seconds - Math.round(seconds)) < 1e-7)
  || t("recipe.step-duration-invalid");
}

function updateDuration(event: Event) {
  const field = event.target as HTMLInputElement;
  // Number inputs expose incomplete entries (e.g. "1e" or "-") as "".
  // Keep this state separate from a deliberate empty entry, including on Save.
  badInput.value = field.validity.badInput;
  const value = field.value;
  if (validDuration(value) !== true) return;
  emit("update:modelValue", Math.round(secondsFromMinutes(value)) || null);
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
