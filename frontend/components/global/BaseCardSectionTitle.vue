<template>
  <v-card
    color="background"
    flat
    class="pb-2"
    :class="{
      'mt-8': section,
    }"
  >
    <v-card-title class="text-h5 pl-0 py-0" style="font-weight: normal;">
      <v-icon
        v-if="icon"
        size="small"
        start
      >
        {{ icon }}
      </v-icon>
      {{ title }}
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

<script lang="ts">
export default defineNuxtComponent({
  props: {
    title: {
      type: String,
      required: true,
    },
    icon: {
      type: String,
      default: "",
    },
    section: {
      type: Boolean,
      default: false,
    },
  },
});
</script>
