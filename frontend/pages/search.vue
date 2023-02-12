<template>
  <v-container fluid class="pa-0">
    <div class="search-container py-8">
      <form class="search-box" @submit.prevent="search">
        <div class="d-flex justify-center my-2">
          <v-text-field
            v-model="state.search"
            outlined
            autofocus
            hide-details
            clearable
            color="primary"
            :placeholder="$tc('search.search-placeholder')"
            :prepend-inner-icon="$globals.icons.search"
          />
        </div>
        <div class="search-row">
          <SearchFilter v-if="categories" v-model="selectedCategories" :items="categories">
            <v-icon left>
              {{ $globals.icons.tags }}
            </v-icon>
            {{ $t("category.categories") }}
            <template v-if="selectedCategories.length > 0">({{ selectedCategories.length }}) </template>
          </SearchFilter>
          <SearchFilter v-if="tags" v-model="selectedTags" :items="tags">
            <v-icon left>
              {{ $globals.icons.tags }}
            </v-icon>
            {{ $t("tag.tags") }}
            <template v-if="selectedTags.length > 0">({{ selectedTags.length }}) </template>
          </SearchFilter>
          <SearchFilter v-if="tools" v-model="selectedTools" :items="tools">
            <v-icon left>
              {{ $globals.icons.tools }}
            </v-icon>
            {{ $t("tool.tools") }}
            <template v-if="selectedTools.length > 0">({{ selectedTools.length }}) </template>
          </SearchFilter>
          <SearchFilter v-if="foods" v-model="selectedFoods" :items="foods">
            <v-icon left>
              {{ $globals.icons.foods }}
            </v-icon>
            {{ $t("general.foods") }}
            <template v-if="selectedFoods.length > 0">({{ selectedFoods.length }}) </template>
          </SearchFilter>
          <v-menu offset-y bottom left nudge-bottom="3" :close-on-content-click="false">
            <template #activator="{ on, attrs }">
              <v-btn class="ml-auto" small color="accent" dark v-bind="attrs" v-on="on">
                <v-icon small>
                  {{ $globals.icons.cog }}
                </v-icon>
              </v-btn>
            </template>
            <v-card>
              <v-card-text>
                <v-text-field
                  v-model="state.maxResults"
                  class="mt-0 pt-0"
                  :label="$tc('search.max-results')"
                  type="number"
                  outlined
                  dense
                />
                <v-btn block color="primary" @click="reset"> Reset </v-btn>
              </v-card-text>
            </v-card>
          </v-menu>
        </div>
        <div class="search-button-container">
          <v-btn x-large color="primary" type="submit" block>
            <v-icon left>
              {{ $globals.icons.search }}
            </v-icon>
            Search
          </v-btn>
        </div>
      </form>
    </div>
    <v-divider></v-divider>
    <v-container class="mt-6 px-md-6">
      <RecipeCardSection
        class="mt-n5"
        :icon="$globals.icons.search"
        :title="$tc('search.results')"
        :recipes="state.results"
      />
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { ref, defineComponent, useRouter, onMounted } from "@nuxtjs/composition-api";
import SearchFilter from "~/components/Domain/SearchFilter.vue";
import { useUserApi } from "~/composables/api";
import { useCategoryStore, useFoodStore, useTagStore, useToolStore } from "~/composables/store";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { IngredientFood, RecipeCategory, RecipeSummary, RecipeTag, RecipeTool } from "~/lib/api/types/recipe";
import { NoUndefinedField } from "~/lib/api/types/non-generated";

export default defineComponent({
  components: { SearchFilter, RecipeCardSection },
  setup() {
    const router = useRouter();
    const api = useUserApi();

    const state = ref({
      search: "",
      maxResults: 21,
      results: [] as RecipeSummary[],
    });

    const categories = useCategoryStore();
    const selectedCategories = ref<NoUndefinedField<RecipeCategory>[]>([]);

    const foods = useFoodStore();
    const selectedFoods = ref<IngredientFood[]>([]);

    const tags = useTagStore();
    const selectedTags = ref<NoUndefinedField<RecipeTag>[]>([]);

    const tools = useToolStore();
    const selectedTools = ref<NoUndefinedField<RecipeTool>[]>([]);

    function reset() {
      state.value.search = "";
      state.value.maxResults = 21;
      selectedCategories.value = [];
      selectedFoods.value = [];
      selectedTags.value = [];
      selectedTools.value = [];

      router.push({
        query: {},
      });

      search();
    }

    function toIDArray(array: { id: string }[]) {
      return array.map((item) => item.id);
    }

    async function search() {
      await router.push({
        query: {
          search: state.value.search,
          maxResults: state.value.maxResults.toString(),
          categories: toIDArray(selectedCategories.value),
          foods: toIDArray(selectedFoods.value),
          tags: toIDArray(selectedTags.value),
          tools: toIDArray(selectedTools.value),
        },
      });

      const { data, error } = await api.recipes.search({
        search: state.value.search,
        page: 1,
        perPage: state.value.maxResults,
        categories: toIDArray(selectedCategories.value),
        foods: toIDArray(selectedFoods.value),
        tags: toIDArray(selectedTags.value),
        tools: toIDArray(selectedTools.value),
      });

      if (error) {
        console.error(error);
        state.value.results = [];
        return;
      }

      if (data) {
        state.value.results = data.items;
      }
    }

    function waitUntilAndExecute(
      condition: () => boolean,
      callback: () => void,
      opts = { timeout: 2000, interval: 500 }
    ): Promise<void> {
      return new Promise((resolve, reject) => {
        const state = {
          timeout: undefined as number | undefined,
          interval: undefined as number | undefined,
        };

        const check = () => {
          if (condition()) {
            clearInterval(state.interval);
            clearTimeout(state.timeout);
            callback();
            resolve();
          }
        };

        // For some reason these were returning NodeJS.Timeout
        state.interval = setInterval(check, opts.interval) as unknown as number;
        state.timeout = setTimeout(() => {
          clearInterval(state.interval);
          reject(new Error("Timeout"));
        }, opts.timeout) as unknown as number;
      });
    }

    onMounted(() => {
      // Hydrate Search
      // wait for stores to be hydrated

      // read query params
      const query = router.currentRoute.query;

      if (query.search) {
        state.value.search = query.search as string;
      }

      if (query.maxResults) {
        state.value.maxResults = parseInt(query.maxResults as string);
      }

      const catProm = waitUntilAndExecute(
        () => categories.items.value.length > 0,
        () => {
          if (query.categories) {
            const result = categories.items.value.filter((item) =>
              (query.categories as string[]).includes(item.id as string)
            );

            selectedCategories.value = result as NoUndefinedField<RecipeCategory>[];
          }
        }
      );

      const foodProm = waitUntilAndExecute(
        () => {
          if (foods.foods.value) {
            return foods.foods.value.length > 0;
          }
          return false;
        },
        () => {
          if (query.foods) {
            const result = foods.foods.value?.filter((item) => (query.foods as string[]).includes(item.id));
            selectedFoods.value = result ?? [];
          }
        }
      );

      const tagsProm = waitUntilAndExecute(
        () => tags.items.value.length > 0,
        () => {
          if (query.tags) {
            const results = tags.items.value.filter((item) => (query.tags as string[]).includes(item.id as string));
            selectedTags.value = results as NoUndefinedField<RecipeTag>[];
          }
        }
      );

      const toolsProm = waitUntilAndExecute(
        () => tools.items.value.length > 0,
        () => {
          if (query.tools) {
            const result = tools.items.value.filter((item) => (query.tools as string[]).includes(item.id));
            selectedTools.value = result as NoUndefinedField<RecipeTool>[];
          }
        }
      );

      Promise.allSettled([catProm, foodProm, tagsProm, toolsProm]).then(() => {
        search();
      });
    });

    return {
      search,
      reset,
      state,
      categories: categories.items as unknown as NoUndefinedField<RecipeCategory>[],
      tags: tags.items as unknown as NoUndefinedField<RecipeTag>[],
      foods: foods.foods,
      tools: tools.items as unknown as NoUndefinedField<RecipeTool>[],

      selectedCategories,
      selectedFoods,
      selectedTags,
      selectedTools,
    };
  },
});
</script>

<style lang="css">
.search-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.search-container {
  display: flex;
  justify-content: center;
}

.search-box {
  width: 950px;
}

.search-button-container {
  margin: 3rem auto 0 auto;
  max-width: 500px;
}
</style>
