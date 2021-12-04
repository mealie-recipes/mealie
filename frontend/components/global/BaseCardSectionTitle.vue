
<template>
  <v-card
    color="background"
    flat
    class="pb-2"
    :class="{
      'mt-8': section,
    }"
  >
    <v-card-title class="headline pl-0 py-0">
      <v-icon v-if="icon !== ''" left>
        {{ icon }}
      </v-icon>
      {{ title }}
    </v-card-title>
    <v-card-text v-if="$slots.default" class="pt-2 pl-0">
      <p class="pb-0 mb-0">
        <slot />
      </p>
    </v-card-text>
    <v-divider class="mb-3"></v-divider>
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
    section: {
      type: Boolean,
      default: false,
    },
  },
};
</script>
