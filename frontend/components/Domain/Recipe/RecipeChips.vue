<template>
  <div v-if="items.length > 0">
    <h2 v-if="title" class="mt-4">{{ title }}</h2>
    <v-chip
      v-for="category in items.slice(0, limit)"
      :key="category"
      label
      class="ma-1"
      color="accent"
      :small="small"
      dark
      :to="`/recipes/${urlParam}/${getSlug(category)}`"
    >
      {{ truncateText(category) }}
    </v-chip>
  </div>
</template>

<script>
export default {
  props: {
    truncate: {
      type: Boolean,
      default: false,
    },
    items: {
      type: Array,
      default: () => [],
    },
    title: {
      type: Boolean,
      default: false,
    },
    isCategory: {
      type: Boolean,
      default: true,
    },
    limit: {
      type: Number,
      default: 999,
    },
    small: {
      type: Boolean,
      default: false,
    },
    maxWidth: {
      type: String,
      default: null,
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
        const matches = this.allCategories.filter((x) => x.name === name);
        if (matches.length > 0) return matches[0].slug;
      } else {
        const matches = this.allTags.filter((x) => x.name === name);
        if (matches.length > 0) return matches[0].slug;
      }
    },
    truncateText(text, length = 20, clamp) {
      if (!this.truncate) return text;
      clamp = clamp || "...";
      const node = document.createElement("div");
      node.innerHTML = text;
      const content = node.textContent;
      return content.length > length ? content.slice(0, length) + clamp : content;
    },
  },
};
</script>

<style></style>
