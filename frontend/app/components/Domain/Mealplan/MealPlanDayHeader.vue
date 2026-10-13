<template>
  <div class="plan-day-header">
    <div class="plan-day-header__text">
      <span class="plan-day-header__weekday" :class="{ 'plan-day-header__weekday--today': today }">
        {{ weekday }}
      </span>
      <span class="plan-day-header__date">{{ date }}</span>
    </div>
    <slot />
  </div>
</template>

<script setup lang="ts">
import { isSameDay } from "date-fns";

interface Props {
  day: Date;
};
const props = defineProps<Props>();

const i18n = useI18n();
const today = computed(() => isSameDay(props.day, new Date()));
const date = computed(() =>
  new Intl.DateTimeFormat(i18n.locale.value, { month: "long", day: "numeric" }).format(props.day),
);
const weekday = computed(() =>
  new Intl.DateTimeFormat(i18n.locale.value, { weekday: "long" }).format(props.day),
);
</script>

<style scoped>
.plan-day-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 44px;
}

.plan-day-header__text {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.plan-day-header__weekday {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--mealie-text-tertiary);
}

.plan-day-header__weekday--today {
  color: rgb(var(--v-theme-primary));
}

.plan-day-header__date {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--mealie-ink);
}
</style>
