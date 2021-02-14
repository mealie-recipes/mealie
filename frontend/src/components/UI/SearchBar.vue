<template>
  <div>
    <v-autocomplete
      :items="autoResults"
      v-model="searchSlug"
      item-value="item.slug"
      item-text="item.name"
      dense
      light
      :label="$t('search.search-mealie')"
      :search-input.sync="search"
      hide-no-data
      cache-items
      solo
      autofocus
      auto-select-first
    >
      <template
        v-if="showResults"
        v-slot:item="{ item }"
        style="max-width: 750px"
      >
        <v-list-item-avatar>
          <v-img :src="getImage(item.item.image)"></v-img>
        </v-list-item-avatar>
        <v-list-item-content @click="selected(item.item.slug)">
          <v-list-item-title>
            {{ item.item.name }}
            <v-rating
              dense
              v-if="item.item.rating"
              :value="item.item.rating"
              size="12"
            >
            </v-rating>
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ item.item.description }}
          </v-list-item-subtitle>
        </v-list-item-content>
      </template>
    </v-autocomplete>
  </div>
</template>

<script>
import Fuse from "fuse.js";
import utils from "@/utils";

export default {
  props: {
    showResults: {
      default: false,
    },
  },
  data() {
    return {
      searchSlug: "",
      search: " ",
      data: [],
      result: [],
      autoResults: [],
      isDark: false,
      options: {
        shouldSort: true,
        threshold: 0.6,
        location: 0,
        distance: 100,
        maxPatternLength: 32,
        minMatchCharLength: 1,
        keys: ["name", "slug", "description"],
      },
    };
  },
  mounted() {
    this.isDark = this.$store.getters.getIsDark;
    this.data = this.$store.getters.getRecentRecipes;
  },
  computed: {
    fuse() {
      return new Fuse(this.data, this.options);
    },
  },
  watch: {
    search() {
      try {
        this.result = this.fuse.search(this.search.trim());
      } catch {
        this.result = this.data
          .map(x => ({ item: x }))
          .sort((a, b) => (a.name > b.name ? 1 : -1));
      }
      console.log(this.result);
      this.$emit("results", this.result);

      if (this.showResults === true) {
        this.autoResults = this.result;
      }
    },
    searchSlug() {
      this.selected(this.searchSlug);
    },
  },
  methods: {
    getImage(image) {
      return utils.getImageURL(image);
    },
    selected(slug) {
      this.$emit("selected", slug);
    },
  },
};
</script>

<style>
.color-transition {
  transition: background-color 0.3s ease;
}
</style>