<template>
  <v-text-field
    v-if="isEditMode"
    v-model="input"
    type="number"
    min="0"
    max="2147483647"
    step="1"
    :label="$t('recipe.step-duration-minutes')"
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
const input = ref<string | number>(props.modelValue ?? "");
watch(() => props.modelValue, value => input.value = value ?? "");

function validDuration(value: string | number | null) {
  if (value === "" || value === null) return true;
  const minutes = Number(value);
  return (Number.isInteger(minutes) && minutes >= 0 && minutes <= 2147483647)
    || t("recipe.step-duration-invalid");
}

function updateDuration(value: string | number | null) {
  if (validDuration(value) !== true) return;
  emit("update:modelValue", Number(value) || null);
}

const formattedDuration = computed(() => {
  const minutes = props.modelValue ?? 0;
  const hours = Math.floor(minutes / 60);
  const remainder = minutes % 60;
  if (!hours) return t("recipe.step-duration-value-minutes", { minutes });
  if (!remainder) return t("recipe.step-duration-value-hours", { hours });
  return t("recipe.step-duration-value", { hours, minutes: remainder });
});
</script>
