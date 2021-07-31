<template>
  <v-card flat class="pb-2">
    <h2>{{ title }}</h2>
    <p class="pb-0 mb-0">
      <slot />
    </p>
  </v-card>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      default: "Place Holder"
    }
  }
}
</script>
