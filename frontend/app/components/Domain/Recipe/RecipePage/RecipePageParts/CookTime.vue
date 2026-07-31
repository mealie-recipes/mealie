<template>
  <div v-if="isEditMode && time" style="width: fit-content;">
    <div>
      {{ $t('recipe.perform-time') }}
    </div>
    <div class="d-flex ga-1 align-center">
      <v-number-input
        v-model="hour"
        class="flex-grow-0"
        style="min-width: 125px;"
        :label="$t('general.hour')"
        control-variant="stacked"
        hide-details
        density="compact"
        inline
        :min="0"
      />
      <v-number-input
        v-model="minute"
        class="flex-grow-0"
        style="min-width: 125px;"
        :label="$t('general.minute')"
        density="compact"
        control-variant="stacked"
        hide-details
        inline
        :min="0"
        :max="60"
        :step="5"
      />
      <v-btn
        variant="flat"
        size="small"
        class="rounded-e-pill"
        :icon="$globals.icons.close"
        @click="time = undefined"
      />
    </div>
  </div>
  <div v-else-if="isEditMode">
    <BaseButton
      secondary
      color="info"
      class="rounded-pill"
      @click="time = '0:00'"
    >
      {{ $t('recipe.perform-time') }}
    </BaseButton>
  </div>
  <div v-else-if="time" style="min-width: fit-content;">
    <v-chip color="info" size="large" :prepend-icon="$globals.icons.clockOutline">
      {{ time }}
    </v-chip>
  </div>
</template>

<script setup lang="ts">
defineProps<{ isEditMode: boolean }>();
const time = defineModel<string | null | undefined>();

const hour = computed({
  get() {
    const definiteTime = time.value ?? "0:00";
    const [definiteHour = "0"] = definiteTime.split(":");
    return parseInt(definiteHour);
  },
  set(newVal) {
    time.value = `${newVal}:${minute.value.toString().padStart(2, "0")}`;
  },
});
const minute = computed({
  get() {
    const definiteTime = time.value ?? "0:00";
    const [_, definiteMin = "0"] = definiteTime.split(":");
    return parseInt(definiteMin);
  },
  set(newVal) {
    time.value = `${hour.value}:${newVal.toString().padStart(2, "0")}`;
  },
});
</script>
