<template>
  <v-card color="background" flat class="pb-2">
    <v-card-title class="headline py-0">
      <v-icon v-if="icon !== ''" left>
        {{ icon }}
      </v-icon>
      {{ title }}
    </v-card-title>
    <v-card-text class="pt-2">
      <p class="pb-0 mb-0">
        <slot />
      </p>
    </v-card-text>
    <v-divider class="my-4"></v-divider>
  </v-card>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      default: "Place Holder",
    },
    icon: {
      type: String,
      default: "",
    },
  },
};
</script>
