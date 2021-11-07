<template>
  <v-container fluid>
    <v-container fluid class="pa-0">
      <v-row dense>
        <v-col>
          <v-text-field
            v-model="searchString"
            outlined
            autofocus
            color="primary accent-3"
            :placeholder="$t('search.search-placeholder')"
            :prepend-inner-icon="$globals.icons.search"
            clearable
          >
          </v-text-field>
        </v-col>
        <v-col cols="12" md="2" sm="12">
          <v-text-field
            v-model="maxResults"
            class="mt-0 pt-0"
            :label="$t('search.max-results')"
            type="number"
            outlined
          />
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
    </v-container>
    <v-container>
      <RecipeCardSection
        class="mt-n5"
        :title-icon="$globals.icons.magnify"
        :recipes="showRecipes.slice(0, maxResults)"
        @sort="assignFuzzy"
      />
    </v-container>
  </v-container>
</template>

<script lang="ts">
import Fuse from "fuse.js";
import { defineComponent, toRefs, computed } from "@nuxtjs/composition-api";
import { reactive } from "vue-demi";
import RecipeSearchFilterSelector from "~/components/Domain/Recipe/RecipeSearchFilterSelector.vue";
import RecipeCategoryTagSelector from "~/components/Domain/Recipe/RecipeCategoryTagSelector.vue";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useRecipes, allRecipes, useFoods } from "~/composables/recipes";
import { RecipeSummary } from "~/types/api-types/recipe";
import { Tag } from "~/api/class-interfaces/tags";
import { useRouteQuery } from "~/composables/use-router";

interface GenericFilter {
  exclude: boolean;
  matchAny: boolean;
}

export default defineComponent({
  components: {
    RecipeCategoryTagSelector,
    RecipeSearchFilterSelector,
    RecipeCardSection,
  },
  setup() {
    const { assignSorted } = useRecipes(true);

    // ================================================================
    // Global State

    const state = reactive({
      maxResults: 21,

      // Filters
      includeCategories: [] as string[],
      catFilter: {
        exclude: false,
        matchAny: false,
      } as GenericFilter,

      includeTags: [] as string[],
      tagFilter: {
        exclude: false,
        matchAny: false,
      } as GenericFilter,

      includeFoods: [] as string[],
      foodFilter: {
        exclude: false,
        matchAny: false,
      } as GenericFilter,

      // Recipes Holders
      searchResults: [] as RecipeSummary[],
      sortedResults: [] as RecipeSummary[],

      // Search Options
      options: {
        shouldSort: true,
        threshold: 0.6,
        location: 0,
        distance: 100,
        findAllMatches: true,
        maxPatternLength: 32,
        minMatchCharLength: 2,
        keys: ["name", "description", "recipeIngredient.note", "recipeIngredient.food.name"],
      },
    });

    // ================================================================
    // Search Functions

    const searchString = useRouteQuery("q", "");

    const filteredRecipes = computed(() => {
      if (!allRecipes.value) {
        return [];
      }
      // TODO: Fix Type Declarations for RecipeSummary
      return allRecipes.value.filter((recipe: RecipeSummary) => {
        const includesTags = check(
          state.includeTags,

          // @ts-ignore
          recipe.tags.map((x: Tag) => x.name),
          state.tagFilter.matchAny,
          state.tagFilter.exclude
        );
        const includesCats = check(
          state.includeCategories,

          // @ts-ignore

          recipe.recipeCategory.map((x) => x.name),
          state.catFilter.matchAny,
          state.catFilter.exclude
        );
        const includesFoods = check(
          state.includeFoods,

          // @ts-ignore
          recipe.recipeIngredient.map((x) => x?.food?.name || ""),
          state.foodFilter.matchAny,
          state.foodFilter.exclude
        );
        return [includesTags, includesCats, includesFoods].every((x) => x === true);
      });
    });

    const fuse = computed(() => {
      return new Fuse(filteredRecipes.value, state.options);
    });

    const fuzzyRecipes = computed(() => {
      if (searchString.value.trim() === "") {
        return filteredRecipes.value;
      }
      const result = fuse.value.search(searchString.value.trim());
      return result.map((x) => x.item);
    });

    const showRecipes = computed(() => {
      if (state.sortedResults.length > 0) {
        return state.sortedResults;
      } else {
        return fuzzyRecipes.value;
      }
    });

    // ================================================================
    // Utility Functions

    function check(filterBy: string[], recipeList: string[], matchAny: boolean, exclude: boolean) {
      let isMatch = true;
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
    }

    function assignFuzzy(val: RecipeSummary[]) {
      state.sortedResults = val;
    }
    function updateTagParams(params: GenericFilter) {
      state.tagFilter = params;
    }
    function updateCatParams(params: GenericFilter) {
      state.catFilter = params;
    }
    function updateFoodParams(params: GenericFilter) {
      state.foodFilter = params;
    }

    const { foods } = useFoods();

    return {
      ...toRefs(state),
      allRecipes,
      assignFuzzy,
      assignSorted,
      check,
      foods,
      searchString,
      showRecipes,
      updateCatParams,
      updateFoodParams,
      updateTagParams,
    };
  },
  head() {
    return {
      title: this.$t("search.search") as string,
    };
  },
});
</script>

<style></style>
