<template>
  <v-menu
    v-model="menuModel"
    readonly
    offset-y
    offset-overflow
    max-height="75vh"
  >
    <template #activator="{ attrs }">
      <v-text-field
        ref="searchInput"
        class="my-auto pt-1"
        v-model="search"
        v-bind="attrs"
        :dense="dense"
        light
        dark
        flat
        :placeholder="$t('search.search-mealie')"
        background-color="primary lighten-1"
        color="white"
        :solo="solo"
        :style="`max-width: ${maxWidth};`"
        @focus="onFocus"
        @blur="isFocused = false"
        autocomplete="off"
        :autofocus="autofocus"
      >
        <template #prepend-inner>
          <v-icon color="grey lighten-3" size="29">
            mdi-magnify
          </v-icon>
        </template>
      </v-text-field>
    </template>
    <v-card
      v-if="showResults"
      max-height="75vh"
      :max-width="maxWidth"
      scrollable
    >
      <v-card-text class="flex row mx-auto ">
        <div class="mr-auto">
          Results
        </div>
        <router-link to="/search"> Advanced Search </router-link>
      </v-card-text>
      <v-divider></v-divider>
      <v-list scrollable v-if="autoResults">
        <v-list-item
          v-for="(item, index) in autoResults.slice(0, 15)"
          :key="index"
          :to="navOnClick ? `/recipe/${item.item.slug}` : null"
          @click="navOnClick ? null : selected(item.item.slug, item.item.name)"
        >
          <v-list-item-avatar>
            <v-img :src="getImage(item.item.slug)"></v-img>
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
import { api } from "@/api";

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
    solo: {
      default: true,
    },
    autofocus: {
      default: false,
    },
  },
  data() {
    return {
      isFocused: false,
      searchSlug: "",
      search: "",
      menuModel: false,
      result: [],
      fuseResults: [],
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
    document.addEventListener("keydown", this.onDocumentKeydown);
  },
  beforeDestroy() {
    document.removeEventListener("keydown", this.onDocumentKeydown);
  },
  computed: {
    data() {
      return this.$store.getters.getAllRecipes;
    },
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
      val ? (this.menuModel = true) : this.resetSearch();
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
      return api.recipes.recipeTinyImage(image);
    },
    selected(slug, name) {
      this.$emit("selected", slug, name);
    },
    async onFocus() {
      this.$store.dispatch("requestAllRecipes");
      this.isFocused = true;
    },
    resetSearch() {
      this.$nextTick(() => {
        this.search = "";
        this.isFocused = false;
        this.menuModel = false;
      });
    },
    onDocumentKeydown(e) {
      if (
        e.key === "/" &&
        e.target !== this.$refs.searchInput.$refs.input &&
        !document.activeElement.id.startsWith("input")
      ) {
        e.preventDefault();
        this.$refs.searchInput.focus();
      }
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
.v-menu__content
  width: 100
  &, & > *
    display: flex
    flex-direction: column
</style>