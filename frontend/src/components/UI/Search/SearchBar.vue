<template>
  <v-menu v-model="menuModel" offset-y readonly max-width="450">
    <template #activator="{ attrs }">
      <v-text-field
        class="mt-6"
        v-model="search"
        v-bind="attrs"
        dense
        light
        :label="$t('search.search-mealie')"
        solo
        autofocus
        style="max-width: 450px;"
        @focus="onFocus"
      >
      </v-text-field>
    </template>
    <v-card  v-if="showResults" max-height="500" min-width="98%" class="">
      <v-card-text  class="py-1">Results</v-card-text>
      <v-divider></v-divider>
      <v-list scrollable>
        <v-list-item
          v-for="(item, index) in autoResults"
          :key="index"
          :to="showResults ? `/recipe/${item.item.slug}` : null"
        >
          <v-list-item-avatar>
            <v-img :src="getImage(item.item.image)"></v-img>
          </v-list-item-avatar>
          <v-list-item-content
            @click="showResults ? null : selected(item.item.slug)"
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
  },
  data() {
    return {
      searchSlug: "",
      search: "",
      menuModel: false,
      data: [],
      result: [],
      autoResults: [],
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
        this.autoResults = this.result;
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
    selected(slug) {
      this.$emit("selected", slug);
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