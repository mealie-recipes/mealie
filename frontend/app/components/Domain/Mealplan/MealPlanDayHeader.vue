<template>
  <v-card border="primary s-lg opacity-100" class="rounded-sm px-2" style="z-index: 2;">
    <v-container class="px-0 d-flex align-center justify-space-between" height="56px">
      <p :class="`pl-2 ${isToday(day) ? 'text-primary font-weight-bold' : ''}`">
        {{ $d(day, "short") }}
      </p>
      <slot />
    </v-container>
  </v-card>
</template>

<script setup lang="ts">
import { isSameDay } from "date-fns";

interface Props {
  day: Date;
};
defineProps<Props>();

const isToday = (date: Date) => {
  return isSameDay(date, new Date());
};
</script>
