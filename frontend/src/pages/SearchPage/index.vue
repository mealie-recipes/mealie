<template>
  <v-container>
    <CategorySidebar />
    <v-card flat>
      <v-row dense>
        <v-col>
          <v-text-field
            v-model="searchString"
            outlined
            color="primary accent-3"
            placeholder="Placeholder"
            append-icon="mdi-magnify"
          >
          </v-text-field>
        </v-col>
        <v-col cols="12" md="2" sm="12">
          <v-text-field
            class="mt-0 pt-0"
            label="Max Results"
            v-model="maxResults"
            type="number"
            outlined
          />
        </v-col>
      </v-row>

      <v-row dense class="mt-0 flex-row align-center justify-space-around">
        <v-col>
          <h3 class="pl-2 headline mt-0">Category Filter</h3>
          <FilterSelector v-model="catFilterType" class="mb-1" />
          <CategorySelector
            :solo="true"
            :dense="false"
            v-model="includeCategories"
            :return-object="false"
          />
        </v-col>
        <v-col>
          <h3 class="pl-2 headline">Tag Filter</h3>
          <FilterSelector v-model="tagFilterType" class="mb-1" />
          <TagSelector
            :solo="true"
            :dense="false"
            v-model="includeTags"
            :return-object="false"
          />
        </v-col>
      </v-row>

      <v-row v-if="fuzzyRecipes">
        <v-col
          :sm="6"
          :md="6"
          :lg="4"
          :xl="3"
          v-for="item in fuzzyRecipes.slice(0, maxResults)"
          :key="item.name"
        >
          <RecipeCard
            :name="item.item.name"
            :description="item.item.description"
            :slug="item.item.slug"
            :rating="item.item.rating"
            :image="item.item.image"
            :tags="item.item.tags"
          />
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>

<script>
import Fuse from "fuse.js";
import RecipeCard from "@/components/Recipe/RecipeCard";
import CategorySidebar from "@/components/UI/CategorySidebar";
import CategorySelector from "@/components/FormHelpers/CategorySelector";
import TagSelector from "@/components/FormHelpers/TagSelector";
import FilterSelector from "./FilterSelector.vue";

const INCLUDE = "include";
const EXCLUDE = "exclude";
const ANY = "any";
export default {
  components: {
    RecipeCard,
    CategorySidebar,
    CategorySelector,
    TagSelector,
    FilterSelector,
  },
  data() {
    return {
      searchString: "",
      maxResults: 21,
      searchResults: [],
      catFilterType: "include",
      includeCategories: [],
      tagFilterType: "include",
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
  computed: {
    allRecipes() {
      return this.$store.getters.getRecentRecipes;
    },
    filteredRecipes() {
      return this.allRecipes.filter(recipe => {
        const includesTags = this.checkTags(recipe.tags);
        const includesCats = this.checkCategories(recipe.recipeCategory);
        return [includesTags, includesCats].every(x => x === true);
      });
    },
    fuse() {
      return new Fuse(this.filteredRecipes, this.options);
    },
    fuzzyRecipes() {
      if (this.searchString.trim() === "") {
        return this.filteredRecipes.map(x => ({ item: x }));
      }
      const result = this.fuse.search(this.searchString.trim());
      return result;
    },
    isSearching() {
      return this.searchString && this.searchString.length > 0;
    },
  },
  methods: {
    checkIncludes(filterBy, recipeList) {
      if (recipeList) {
        return filterBy.every(t => recipeList.includes(t));
      } else;
      return false;
    },

    checkExcludes(filterBy, recipeList) {
      if (recipeList) {
        return filterBy.every(t => !recipeList.includes(t));
      } else;
      return false;
    },

    checkAny(filterBy, recipeList) {
      if (filterBy.length === 0) return true;
      if (recipeList) {
        return filterBy.some(t => recipeList.includes(t));
      } else;
      return false;
    },

    checkTags(recipeTags) {
      if (this.tagFilterType === INCLUDE) {
        return this.checkIncludes(this.includeTags, recipeTags);
      }
      if (this.tagFilterType === EXCLUDE) {
        return this.checkExcludes(this.includeTags, recipeTags);
      }
      if (this.tagFilterType === ANY) {
        return this.checkAny(this.includeTags, recipeTags);
      }
    },

    checkCategories(recipeCategories) {
      if (this.catFilterType === INCLUDE) {
        return this.checkIncludes(this.includeCategories, recipeCategories);
      }
      if (this.catFilterType === EXCLUDE) {
        return this.checkExcludes(this.includeCategories, recipeCategories);
      }
      if (this.catFilterType === ANY) {
        return this.checkAny(this.includeCategories, recipeCategories);
      }
    },
  },
};
</script>

<style>
</style>