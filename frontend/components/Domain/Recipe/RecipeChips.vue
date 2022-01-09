<template>
  <div v-if="items.length > 0">
    <h2 v-if="title" class="mt-4">{{ title }}</h2>
    <v-chip
      v-for="category in items.slice(0, limit)"
      :key="category.name"
      label
      class="ma-1"
      color="accent"
      :small="small"
      dark
      :to="`/recipes/${urlParam}/${category.slug}`"
    >
      {{ truncateText(category.name) }}
    </v-chip>
  </div>
</template>

<script lang="ts">
import {computed, defineComponent} from "@nuxtjs/composition-api";

export default defineComponent({
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
  setup(props) {
    const urlParam = computed(() => props.isCategory ? "categories" : "tags");

    function truncateText(text: string, length = 20, clamp = "...") {
      if (!props.truncate) return text;
      const node = document.createElement("div");
      node.innerHTML = text;
      const content = node.textContent || "";
      return content.length > length ? content.slice(0, length) + clamp : content;
    }

    return {
      urlParam,
      truncateText,
    }
  },
});
</script>

<style></style>
