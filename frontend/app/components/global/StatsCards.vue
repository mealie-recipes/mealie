<template>
  <component
    :is="to ? NuxtLink : 'div'"
    :to="to || undefined"
    class="stats-tile"
    :class="{ 'stats-tile--link': !!to }"
    :style="minWidth ? { minWidth: /^\d+$/.test(minWidth) ? `${minWidth}px` : minWidth } : undefined"
  >
    <span class="stats-tile__icon">
      <v-icon size="18">{{ activeIcon }}</v-icon>
    </span>
    <span class="stats-tile__text">
      <span class="stats-tile__value"><slot name="value" /></span>
      <span class="stats-tile__label"><slot name="title" /></span>
    </span>
  </component>
</template>

<script setup lang="ts">
const props = defineProps({
  icon: {
    type: String,
    default: null,
  },
  minWidth: {
    type: String,
    default: "",
  },
  to: {
    type: String,
    default: null,
  },
});

const { $globals } = useNuxtApp();
const NuxtLink = resolveComponent("NuxtLink");

const activeIcon = computed(() => {
  return props.icon ?? $globals.icons.primary;
});
</script>

<style scoped>
.stats-tile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px 12px 12px;
  border-radius: 16px;
  background: var(--mealie-surface);
  box-shadow: inset 0 0 0 1px var(--mealie-hairline);
  color: var(--mealie-ink);
  text-decoration: none;
}

.stats-tile--link:hover {
  box-shadow:
    inset 0 0 0 1px var(--mealie-hairline-strong),
    0 10px 24px -18px rgba(40, 30, 20, 0.4);
}

.stats-tile__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  border-radius: 10px;
  background: rgba(var(--v-theme-primary), 0.1);
  color: rgb(var(--v-theme-primary));
}

.stats-tile__text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.stats-tile__value {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}

.stats-tile__label {
  font-size: 13px;
  color: var(--mealie-text-tertiary);
  white-space: nowrap;
}
</style>
