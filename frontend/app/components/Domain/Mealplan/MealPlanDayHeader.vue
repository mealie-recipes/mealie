<template>
  <v-card
    border="primary s-lg opacity-100"
    class="rounded-sm px-2"
    style="z-index: 2;"
    :color="endDate ? 'primary' : undefined"
    :variant="endDate ? 'tonal' : undefined"
  >
    <v-container class="px-0 d-flex align-center justify-space-between" height="56px">
      <p :class="`pl-2 ${isCurrent ? 'text-primary font-weight-bold' : ''}`">
        {{ $d(day, "short") }}<template v-if="endDate">
          - {{ $d(endDate, "short") }}
        </template>
      </p>
      <slot />
    </v-container>
  </v-card>
</template>

<script setup lang="ts">
import { endOfDay, isSameDay, isWithinInterval, startOfDay } from "date-fns";

interface Props {
  day: Date;
  /** Set for a week, whose meals aren't planned for a specific day */
  endDate?: Date | null;
};
const props = defineProps<Props>();

const isCurrent = computed(() => {
  const today = new Date();
  return props.endDate
    ? isWithinInterval(today, { start: startOfDay(props.day), end: endOfDay(props.endDate) })
    : isSameDay(props.day, today);
});
</script>
