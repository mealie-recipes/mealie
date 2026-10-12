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
    @update:model-value="updateDuration"
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

function validDuration(value: string | number | null) {
  if (value === "" || value === null) return true;
  const seconds = Number(value) * 60;
  // Permit floating-point representation noise, never a fractional second.
  return (Number.isFinite(seconds) && seconds >= 0 && seconds <= 2147483647
    && Math.abs(seconds - Math.round(seconds)) < 1e-7)
  || t("recipe.step-duration-invalid");
}

function updateDuration(value: string | number | null) {
  if (validDuration(value) !== true) return;
  emit("update:modelValue", Math.round(Number(value) * 60) || null);
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
