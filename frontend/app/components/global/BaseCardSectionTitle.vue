<template>
  <v-card
    color="background"
    flat
    class="pb-2"
    :class="{
      'mt-8': section,
    }"
  >
    <v-card-title :class="`text-title-${size} pl-0 py-0 d-flex align-center`" style="font-weight: normal;">
      <slot name="prepend-title" />
      <v-icon
        v-if="icon"
        size="small"
        start
      >
        {{ icon }}
      </v-icon>
      {{ title }}
      <slot name="append-title" />
    </v-card-title>
    <v-card-text
      v-if="$slots.default"
      class="pt-2 pl-0"
    >
      <p class="pb-0 mb-0">
        <slot />
      </p>
    </v-card-text>
    <v-divider class="mt-1 mb-3" />
  </v-card>
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
