<template>
  <v-text-field
    v-if="isEditMode"
    v-model="input"
    class="step-duration"
    type="number"
    min="0"
    max="35791394"
    step="1"
    :hint="modelValue && modelValue % 60 ? $t('recipe.step-duration-saved', { duration: formattedDuration }) : undefined"
    persistent-hint
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
import { wholeNumber } from "~/lib/validators/inputs";

const props = defineProps<{
  modelValue?: number | null;
  isEditMode: boolean;
}>();
const emit = defineEmits<{ "update:modelValue": [value: number | null] }>();
const { t } = useI18n();
// Display whole minutes only; keep imported seconds untouched until an input event.
// The hint exposes any remainder before the user deliberately replaces it.
const input = ref<string | number>(props.modelValue ? Math.floor(props.modelValue / 60) : "");
watch(() => props.modelValue, value => input.value = value ? Math.floor(value / 60) : "");

const badInput = ref(false);

function validDuration(value: string | number | null) {
  if (badInput.value || Number(value) > 35791394) return t("validators.whole-number");
  return wholeNumber(value);
}

function updateDuration(event: Event) {
  const field = event.target as HTMLInputElement;
  // Number inputs expose incomplete entries (e.g. "1e" or "-") as "".
  // Keep this state separate from a deliberate empty entry, including on Save.
  badInput.value = field.validity.badInput;
  const value = field.value;
  if (validDuration(value) !== true) return;
  emit("update:modelValue", Number(value) * 60 || null);
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
