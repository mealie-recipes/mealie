<template>
  <v-container>
    <v-row dense>
      <v-col>
        <v-text-field
          v-model="searchString"
          outlined
          color="primary accent-3"
          :placeholder="$t('search.search-placeholder')"
          :append-icon="$globals.icons.search"
        >
        </v-text-field>
      </v-col>
      <v-col cols="12" md="2" sm="12">
        <v-text-field v-model="maxResults" class="mt-0 pt-0" :label="$t('search.max-results')" type="number" outlined />
      </v-col>
    </v-row>

    <ToggleState>
      <template #activator="{ state, toggle }">
        <v-switch :value="state" color="info" class="ma-0 pa-0" label="Advanced" @input="toggle" @click="toggle">
          Advanced
        </v-switch>
      </template>
      <template #default="{ state }">
        <v-expand-transition>
          <v-row v-show="state" dense class="my-0 dense flex-row align-center justify-space-around">
            <v-col>
              <h3 class="pl-2 text-center headline">
                {{ $t("category.category-filter") }}
              </h3>
              <RecipeSearchFilterSelector class="mb-1" @update="updateCatParams" />
              <RecipeCategoryTagSelector
                v-model="includeCategories"
                :solo="true"
                :dense="false"
                :return-object="false"
              />
            </v-col>
            <v-col>
              <h3 class="pl-2 text-center headline">
                {{ $t("search.tag-filter") }}
              </h3>
              <RecipeSearchFilterSelector class="mb-1" @update="updateTagParams" />
              <RecipeCategoryTagSelector
                v-model="includeTags"
                :solo="true"
                :dense="false"
                :return-object="false"
                :tag-selector="true"
              />
            </v-col>
            <v-col>
              <h3 class="pl-2 text-center headline">Food Filter</h3>
              <RecipeSearchFilterSelector class="mb-1" @update="updateFoodParams" />
              <v-autocomplete
                v-model="includeFoods"
                hide-details
                chips
                deletable-chips
                solo
                multiple
                :items="foods || []"
                item-text="name"
                class="mx-1 py-0 mb-8"
                :prepend-inner-icon="$globals.icons.foods"
                label="Choose Food"
                @blur="foodBlur"
              >
                <template #selection="data">
                  <v-chip
                    :key="data.index"
                    class="ma-1"
                    :input-value="data.selected"
                    close
                    label
                    color="accent"
                    dark
                    @click:close="includeFoods.splice(data.index, 1)"
                  >
                    {{ data.item.name || data.item }}
                  </v-chip>
                </template>
              </v-autocomplete>
            </v-col>
          </v-row>
        </v-expand-transition>
      </template>
    </ToggleState>

    <RecipeCardSection
      class="mt-n5"
      :title-icon="$globals.icons.magnify"
      :recipes="showRecipes.slice(0, maxResults)"
      @sort="assignFuzzy"
    />
  </v-container>
</template>

<script lang="ts">
import Fuse from "fuse.js";
import { defineComponent } from "@nuxtjs/composition-api";
import RecipeSearchFilterSelector from "~/components/Domain/Recipe/RecipeSearchFilterSelector.vue";
import RecipeCategoryTagSelector from "~/components/Domain/Recipe/RecipeCategoryTagSelector.vue";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useRecipes, allRecipes, useFoods } from "~/composables/recipes";
import { RecipeSummary } from "~/types/api-types/recipe";

export default defineComponent({
  components: {
    RecipeCategoryTagSelector,
    RecipeSearchFilterSelector,
    RecipeCardSection,
  },
  setup() {
    const { assignSorted } = useRecipes(true);

    const { foods } = useFoods();

    return { assignSorted, allRecipes, foods };
  },
  data() {
    return {
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
      foodFilters: {
        exclude: false,
        matchAny: false,
      },
      sortedResults: [],
      includeCategories: [],
      includeTags: [],
      includeFoods: [],
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
  // head() {
  //   return {
  //     title: this.$t("search.search"),
  //   };
  // },
  computed: {
    searchString: {
      set(q) {
        this.$router.replace({ query: { ...this.$route.query, q } });
      },
      get() {
        return this.$route.query.q || "";
      },
    },
    filteredRecipes() {
      return this.allRecipes.filter((recipe: RecipeSummary) => {
        const includesTags = this.check(
          this.includeTags,
          recipe.tags.map((x) => x.name),
          this.tagFilter.matchAny,
          this.tagFilter.exclude
        );
        const includesCats = this.check(
          this.includeCategories,
          recipe.recipeCategory.map((x) => x.name),
          this.catFilter.matchAny,
          this.catFilter.exclude
        );

        console.log();

        const includesFoods = this.check(
          this.includeFoods,
          recipe.recipeIngredient.map((x) => x?.food?.name || ""),
          this.foodFilters.matchAny,
          this.foodFilters.exclude
        );
        return [includesTags, includesCats, includesFoods].every((x) => x === true);
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
      return result.map((x) => x.item);
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
      console.log({ filterBy, recipeList, matchAny, exclude });
      if (filterBy.length === 0) return isMatch;

      if (recipeList) {
        if (matchAny) {
          isMatch = filterBy.some((t) => recipeList.includes(t)); // Checks if some items are a match
        } else {
          isMatch = filterBy.every((t) => recipeList.includes(t)); // Checks if every items is a match
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
    updateFoodParams(params) {
      this.foodFilter = params;
    },
    foodBlur() {
      console.log("Food Blur");
    },
  },
});
</script>

<style></style>
