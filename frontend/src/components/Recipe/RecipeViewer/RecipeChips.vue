<template>
  <div v-if="items && items.length > 0">
    <h2 class="mt-4">{{ title }}</h2>
    <v-chip
      class="ma-1"
      color="accent"
      dark
      v-for="category in items"
      :key="category"
    >
      {{ category }}
    </v-chip>
  </div>
</template>

<script>
export default {
  props: {
    items: Array,
    title: String,
  },
};
</script>

<style>
</style>