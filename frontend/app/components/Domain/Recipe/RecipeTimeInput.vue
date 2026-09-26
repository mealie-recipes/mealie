<template>
  <div>
    <div class="text-caption opacity-80">
      {{ label }}
    </div>
    <div
      class="d-flex flex-wrap align-center"
      style="gap: 0 1rem"
    >
      <v-number-input
        v-model="hours"
        :min="0"
        :max="MAX_HOURS"
        :precision="0"
        :suffix="durationUnitLabel('hour')"
        variant="underlined"
        density="compact"
        inset
        class="time-input"
      />
      <v-number-input
        v-model="minutes"
        :min="0"
        :precision="0"
        :suffix="durationUnitLabel('minute')"
        variant="underlined"
        density="compact"
        inset
        class="time-input"
      />
      <!-- Shown after the structured time, e.g. "3 hours" + "plus overnight" -->
      <v-text-field
        v-model="text"
        density="compact"
        variant="underlined"
        class="time-text"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRecipeTime } from "~/composables/recipes";

defineProps<{ label: string }>();

const { durationUnitLabel } = useRecipeTime();

const seconds = defineModel<number | null | undefined>("seconds", { required: true });
const text = defineModel<string | null | undefined>("text", { required: true });

/** Keeps hours, minutes, and any leftover seconds under the database's 2^31 - 1 limit */
const MAX_HOURS = Math.floor((2 ** 31 - 1 - 3599) / 3600);

const hours = ref<number | null>(null);
const minutes = ref<number | null>(null);

function toSeconds(): number | null {
  // Imported times can carry seconds the inputs don't show, which shouldn't be lost on edit
  const leftover = (seconds.value ?? 0) % 60;
  const total = (hours.value ?? 0) * 3600 + (minutes.value ?? 0) * 60 + leftover;
  return total > 0 ? total : null;
}

watch(
  seconds,
  (value) => {
    // Only re-split outside changes, so typing "90" minutes isn't rewritten to 1 hour 30 mid-edit
    if ((value ?? null) === toSeconds()) {
      return;
    }
    hours.value = value ? Math.floor(value / 3600) : null;
    minutes.value = value ? Math.floor((value % 3600) / 60) : null;
  },
  { immediate: true },
);

watch([hours, minutes], () => {
  seconds.value = toSeconds();
});
</script>

<style scoped>
.time-input {
  flex: 1 1 9em;
  max-width: 12em;
}
.time-text {
  flex: 3 1 12em;
}
</style>
