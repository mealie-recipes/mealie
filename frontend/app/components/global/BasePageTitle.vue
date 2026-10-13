<template>
  <div class="base-page-title" :class="{ 'base-page-title--divider': divider }">
    <div v-if="$slots.header" class="base-page-title__header">
      <slot name="header" />
    </div>
    <section class="base-page-title__text">
      <h1 class="base-page-title__title">
        <slot name="title">
          👋 Here's a Title
        </slot>
      </h1>
      <div v-if="$slots.default" class="base-page-title__subtitle">
        <slot />
      </div>
    </section>
    <section v-if="$slots.content" class="base-page-title__content">
      <slot name="content" />
    </section>
  </div>
</template>

<script setup lang="ts">
defineProps({
  divider: {
    type: Boolean,
    default: false,
  },
});
</script>

<style scoped>
.base-page-title {
  margin: 16px 0 8px;
  color: var(--mealie-ink);
}

.base-page-title--divider {
  margin-bottom: 24px;
}

/* the decorative illustrations these headers used to carry give way to the type; anything
   else placed here (an avatar, a back link) still shows */
.base-page-title__header :deep(.v-img) {
  display: none;
}

.base-page-title__header:has(> .v-img:only-child) {
  display: none;
}

.base-page-title__header {
  margin-bottom: 12px;
}

.base-page-title__title {
  margin: 0;
  font-size: 34px;
  font-weight: 700;
  letter-spacing: -0.025em;
  line-height: 1.1;
}

.base-page-title__subtitle {
  max-width: 680px;
  margin: 8px 0 0;
  font-size: 15px;
  line-height: 1.5;
  color: var(--mealie-text-secondary);
}

.base-page-title__content {
  display: flex;
  margin-top: 12px;
}

@media (max-width: 600px) {
  .base-page-title__title {
    font-size: 28px;
  }
}
</style>
