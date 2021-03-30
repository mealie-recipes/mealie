<template>
  <v-menu v-model="menuModel" offset-y readonly :max-width="maxWidth">
    <template #activator="{ attrs }">
      <v-text-field
        class="mt-6"
        v-model="search"
        v-bind="attrs"
        :dense="dense"
        light
        :label="$t('search.search-mealie')"
        autofocus
        :solo="solo"
        :style="`max-width: ${maxWidth};`"
        @focus="onFocus"
        autocomplete="off"
      >
      </v-text-field>
    </template>
    <v-card v-if="showResults" max-height="500" :max-width="maxWidth">
      <v-card-text class="py-1">Results</v-card-text>
      <v-divider></v-divider>
      <v-list scrollable>
        <v-list-item
          v-for="(item, index) in autoResults"
          :key="index"
          :to="navOnClick ? `/recipe/${item.item.slug}` : null"
          @click="navOnClick ? null : selected(item.item.slug, item.item.name)"
        >
          <v-list-item-avatar>
            <v-img :src="getImage(item.item.image)"></v-img>
          </v-list-item-avatar>
          <v-list-item-content
            @click="
              showResults ? null : selected(item.item.slug, item.item.name)
            "
          >
            <v-list-item-title v-html="highlight(item.item.name)">
            </v-list-item-title>
            <v-rating
              dense
              v-if="item.item.rating"
              :value="item.item.rating"
              size="12"
            >
            </v-rating>
            <v-list-item-subtitle v-html="highlight(item.item.description)">
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </v-menu>
</template>

<script>
import Fuse from "fuse.js";
import utils from "@/utils";

export default {
  props: {
    showResults: {
      default: false,
    },
    maxWidth: {
      default: "450px",
    },
    dense: {
      default: true,
    },
    navOnClick: {
      default: true,
    },
    resetSearch: {
      default: false,
    },
    solo: {
      default: true,
    },
  },
  data() {
    return {
      searchSlug: "",
      search: "",
      menuModel: false,
      data: [],
      result: [],
      fuseResults: [],
      isDark: false,
      options: {
        shouldSort: true,
        threshold: 0.6,
        location: 0,
        distance: 100,
        findAllMatches: true,
        maxPatternLength: 32,
        minMatchCharLength: 2,
        keys: ["name", "description"],
      },
    };
  },
  mounted() {
    this.isDark = this.$store.getters.getIsDark;
    this.data = this.$store.getters.getRecentRecipes;
  },
  computed: {
    autoResults() {
      return this.fuseResults.length > 1 ? this.fuseResults : this.results;
    },
    fuse() {
      return new Fuse(this.data, this.options);
    },
    isSearching() {
      return this.search && this.search.length > 0;
    },
  },
  watch: {
    isSearching(val) {
      val ? (this.menuModel = true) : null;
    },

    resetSearch(val) {
      val ? (this.search = "") : null;
    },

    search() {
      try {
        this.result = this.fuse.search(this.search.trim());
      } catch {
        this.result = this.data
          .map(x => ({ item: x }))
          .sort((a, b) => (a.name > b.name ? 1 : -1));
      }
      this.$emit("results", this.result);

      if (this.showResults === true) {
        this.fuseResults = this.result;
      }
    },
    searchSlug() {
      this.selected(this.searchSlug);
    },
  },
  methods: {
    highlight(string) {
      if (!this.search) {
        return string;
      }
      return string.replace(
        new RegExp(this.search, "gi"),
        match => `<mark>${match}</mark>`
      );
    },
    getImage(image) {
      return utils.getImageURL(image);
    },
    selected(slug, name) {
      console.log("Selected", slug, name);
      this.$emit("selected", slug, name);
    },
    async onFocus() {
      clearTimeout(this.timeout);
      this.isFocused = true;
    },
  },
};
</script>

<style scoped>
.color-transition {
  transition: background-color 0.3s ease;
}
</style>

<style lang="sass" scoped>
</style>