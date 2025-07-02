<template>
  <div class="mt-4">
    <section class="d-flex flex-column align-center">
      <slot name="header" />
      <h2 class="text-h5">
        <slot name="title">
          👋 Here's a Title
        </slot>
      </h2>

      <h3 class="subtitle-1">
        <slot />
      </h3>
    </section>
    <section class="d-flex">
      <slot name="content" />
    </section>
    <v-divider
      v-if="divider"
      class="my-4"
    />
  </div>
</template>

<script lang="ts">
export default defineNuxtComponent({
  props: {
    divider: {
      type: Boolean,
      default: false,
    },
  },
});
</script>

<style scoped>
.subtitle-1 {
  font-size: 1rem;
  font-weight: normal;
  color: var(--v-text-caption);
}
</style>
