<template>
  <div
    class="base-section-title"
    :class="[`base-section-title--${size}`, { 'base-section-title--section': section }]"
  >
    <h2 class="base-section-title__title">
      <slot name="prepend-title" />
      <v-icon
        v-if="icon"
        size="small"
        class="base-section-title__icon"
      >
        {{ icon }}
      </v-icon>
      {{ title }}
      <slot name="append-title" />
    </h2>
    <div v-if="$slots.default" class="base-section-title__text">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
type Size = "large" | "medium" | "small";

defineProps({
  title: {
    type: String,
    required: true,
  },
  size: {
    type: String as () => Size,
    default: "large",
  },
  icon: {
    type: String,
    default: "",
  },
  section: {
    type: Boolean,
    default: false,
  },
});
</script>

<style scoped>
.base-section-title {
  padding-bottom: 10px;
  margin-bottom: 14px;
  border-bottom: 1px solid var(--mealie-hairline);
  color: var(--mealie-ink);
}

.base-section-title--section {
  margin-top: 36px;
}

.base-section-title__title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.015em;
}

.base-section-title--medium .base-section-title__title {
  font-size: 17px;
}

.base-section-title--small .base-section-title__title {
  font-size: 15px;
}

.base-section-title__icon {
  color: var(--mealie-icon);
}

.base-section-title__text {
  max-width: 680px;
  margin: 6px 0 0;
  font-size: 14px;
  line-height: 1.5;
  color: var(--mealie-text-secondary);
}
</style>
