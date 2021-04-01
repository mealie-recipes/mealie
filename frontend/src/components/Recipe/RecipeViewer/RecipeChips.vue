<template>
  <div v-if="items && items.length > 0">
    <h2 class="mt-4">{{ title }}</h2>
    <v-chip
      :to="`/recipes/${getSlug(category)}`"
      label
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
    category: {
      default: true,
    },
  },
  computed: {
    allCategories() {
      return this.$store.getters.getAllCategories;
    },
  },
  methods: {
    getSlug(name) {
      if (!name) return;
      if (this.category) {
        const matches = this.allCategories.filter(x => x.name == name);
        if (matches.length > 0) return matches[0].slug;
      }
    },
  },
};
</script>

<style>
</style>