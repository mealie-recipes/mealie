<template>
  <div v-if="items.length > 0">
    <h2 v-if="title" class="mt-4">{{ title }}</h2>
    <v-chip
      label
      class="ma-1"
      color="accent"
      :small="small"
      dark
      v-for="category in items.slice(0, limit)"
      :to="`/recipes/${urlParam}/${getSlug(category)}`"
      :key="category"
    >
      {{ category }}
    </v-chip>
  </div>
</template>

<script>
export default {
  props: {
    items: {
      default: [],
    },
    title: {
      default: null,
    },
    isCategory: {
      default: true,
    },
    limit: {
      default: 999,
    },
    small: {
      default: false,
    },
  },
  computed: {
    allCategories() {
      return this.$store.getters.getAllCategories;
    },
    allTags() {
      return this.$store.getters.getAllTags;
    },
    urlParam() {
      return this.isCategory ? "category" : "tag";
    },
  },
  methods: {
    getSlug(name) {
      if (!name) return;

      if (this.isCategory) {
        const matches = this.allCategories.filter(x => x.name == name);
        if (matches.length > 0) return matches[0].slug;
      } else {
        const matches = this.allTags.filter(x => x.name == name);
        if (matches.length > 0) return matches[0].slug;
      }
    },
  },
};
</script>

<style>
</style>