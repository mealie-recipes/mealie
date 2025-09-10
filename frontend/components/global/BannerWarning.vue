<template>
  <v-alert
    border="start"
    border-color
    variant="tonal"
    type="warning"
    elevation="2"
    :icon="$globals.icons.alert"
  >
    <b v-if="title">{{ title }}</b>
    <div v-if="description">
      {{ description }}
    </div>
    <div
      v-if="$slots.default"
      class="py-2"
    >
      <slot />
    </div>
  </v-alert>
</template>

<script lang="ts">
export default {
  props: {
    title: {
      type: String,
      required: false,
      default: "",
    },
    description: {
      type: String,
      required: false,
      default: "",
    },
  },
};
</script>
