<template>
  <v-container>
    <v-card flat>
      <v-row dense>
        <v-col>
          <v-text-field
            v-model="searchString"
            outlined
            color="primary accent-3"
            :placeholder="$t('search.search-placeholder')"
            append-icon="mdi-magnify"
          >
          </v-text-field>
        </v-col>
        <v-col cols="12" md="2" sm="12">
          <v-text-field
            class="mt-0 pt-0"
            :label="$t('search.max-results')"
            v-model="maxResults"
            type="number"
            outlined
          />
        </v-col>
      </v-row>

      <v-row dense class="mt-0 flex-row align-center justify-space-around">
        <v-col>
          <h3 class="pl-2 text-center headline">
            {{ $t("category.category-filter") }}
          </h3>
          <FilterSelector class="mb-1" @update="updateCatParams" />
          <CategoryTagSelector :solo="true" :dense="false" v-model="includeCategories" :return-object="false" />
        </v-col>
        <v-col>
          <h3 class="pl-2 text-center headline">
            {{ $t("search.tag-filter") }}
          </h3>
          <FilterSelector class="mb-1" @update="updateTagParams" />
          <CategoryTagSelector
            :solo="true"
            :dense="false"
            v-model="includeTags"
            :return-object="false"
            :tag-selector="true"
          />
        </v-col>
      </v-row>

      <CardSection title-icon="mdi-mag" :recipes="showRecipes" :hardLimit="maxResults" @sort="assignFuzzy" />
    </v-card>
  </v-container>
</template>

<script>
import Fuse from "fuse.js";
import CategoryTagSelector from "@/components/FormHelpers/CategoryTagSelector";
import CardSection from "@/components/UI/CardSection";
import FilterSelector from "./FilterSelector.vue";

export default {
  components: {
    CardSection,
    CategoryTagSelector,
    FilterSelector,
  },
  data() {
    return {
      searchString: "",
      maxResults: 21,
      searchResults: [],
      catFilter: {
        exclude: false,
        matchAny: false,
      },
      tagFilter: {
        exclude: false,
        matchAny: false,
      },
      sortedResults: [],
      includeCategories: [],
      includeTags: [],
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
    this.$store.dispatch("requestAllRecipes");
  },
  computed: {
    allRecipes() {
      return this.$store.getters.getAllRecipes;
    },
    filteredRecipes() {
      return this.allRecipes.filter(recipe => {
        const includesTags = this.check(this.includeTags, recipe.tags, this.tagFilter.matchAny, this.tagFilter.exclude);
        const includesCats = this.check(
          this.includeCategories,
          recipe.recipeCategory,
          this.catFilter.matchAny,
          this.catFilter.exclude
        );
        return [includesTags, includesCats].every(x => x === true);
      });
    },
    fuse() {
      return new Fuse(this.filteredRecipes, this.options);
    },
    fuzzyRecipes() {
      if (this.searchString.trim() === "") {
        return this.filteredRecipes;
      }
      const result = this.fuse.search(this.searchString.trim());
      return result.map(x => x.item);
    },
    isSearching() {
      return this.searchString && this.searchString.length > 0;
    },
    showRecipes() {
      if (this.sortedResults.length > 0) {
        return this.sortedResults;
      } else {
        return this.fuzzyRecipes;
      }
    },
  },
  methods: {
    assignFuzzy(val) {
      this.sortedResults = val;
    },
    check(filterBy, recipeList, matchAny, exclude) {
      let isMatch = true;
      if (filterBy.length === 0) return isMatch;

      if (recipeList) {
        if (matchAny) {
          isMatch = filterBy.some(t => recipeList.includes(t)); // Checks if some items are a match
        } else {
          isMatch = filterBy.every(t => recipeList.includes(t)); // Checks if every items is a match
        }
        return exclude ? !isMatch : isMatch;
      } else;
      return false;
    },

    updateTagParams(params) {
      this.tagFilter = params;
    },
    updateCatParams(params) {
      this.catFilter = params;
    },
  },
};
</script>

<style></style>
