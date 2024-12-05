<template>
  <v-container>
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/manage-cookbooks.svg')"></v-img>
      </template>
      <template #title> {{ $tc('recipe-finder.recipe-finder') }} </template>
      {{ $t('recipe-finder.recipe-finder-description') }}
    </BasePageTitle>
    <v-container v-if="ready">
      <v-row>
        <v-col :cols="useMobile ? 12 : 3">
          <v-container class="ma-0 pa-0">
            <v-row no-gutters>
              <v-col cols="12" no-gutters :class="attrs.searchFilter.colClass">
                <SearchFilter v-if="foods" v-model="selectedFoods" :items="foods" :class="attrs.searchFilter.filterClass">
                  <v-icon left>
                    {{ $globals.icons.foods }}
                  </v-icon>
                  {{ $t("general.foods") }}
                </SearchFilter>
                <SearchFilter v-if="tools" v-model="selectedTools" :items="tools" :class="attrs.searchFilter.filterClass">
                  <v-icon left>
                    {{ $globals.icons.potSteam }}
                  </v-icon>
                  {{ $t("tool.tools") }}
                </SearchFilter>
                <div :class="attrs.searchFilter.filterClass">
                  <v-badge
                    :value="queryFilterJSON.parts && queryFilterJSON.parts.length"
                    small
                    overlap
                    color="primary"
                    :content="(queryFilterJSON.parts || []).length"
                  >
                    <v-btn
                      small
                      color="accent"
                      dark
                      @click="queryFilterMenu = !queryFilterMenu"
                    >
                      <v-icon left>
                        {{ $globals.icons.filter }}
                      </v-icon>
                      {{ $tc("recipe-finder.other-filters") }}
                      <BaseDialog
                        v-model="queryFilterMenu"
                        :title="$tc('recipe-finder.other-filters')"
                        :icon="$globals.icons.filter"
                        width="100%"
                        max-width="1100px"
                        :submit-disabled="!queryFilterEditorValue"
                        @confirm="saveQueryFilter"
                      >
                        <QueryFilterBuilder
                          :key="queryFilterMenuKey"
                          :initial-query-filter="queryFilterJSON"
                          :field-defs="queryFilterBuilderFields"
                          @input="(value) => queryFilterEditorValue = value"
                          @inputJSON="(value) => queryFilterEditorValueJSON = value"
                        />
                        <template #custom-card-action>
                          <BaseButton color="error" type="submit" @click="clearQueryFilter">
                            <template #icon>
                              {{ $globals.icons.close }}
                            </template>
                            {{ $t("search.clear-selection") }}
                          </BaseButton>
                        </template>
                      </BaseDialog>
                    </v-btn>
                  </v-badge>
                </div>
              </v-col>
            </v-row>
            <!-- Settings Menu -->
            <v-row no-gutters class="mb-2">
              <v-col cols="12" :class="attrs.settings.colClass">
                <v-menu
                  v-model="settingsMenu"
                  offset-y
                  nudge-bottom="3"
                  :close-on-content-click="false"
                >
                  <template #activator="{ on, attrs: activatorAttrs}">
                    <v-btn small color="primary" dark v-bind="activatorAttrs" v-on="on">
                      <v-icon left>
                        {{ $globals.icons.cog }}
                      </v-icon>
                      {{ $t("general.settings") }}
                    </v-btn>
                  </template>
                  <v-card>
                    <v-card-text>
                      <div>
                        <v-text-field
                          v-model="settings.maxMissingFoods"
                          type="number"
                          hide-details
                          hide-spin-buttons
                          :label="$tc('recipe-finder.max-missing-ingredients')"
                        />
                        <v-text-field
                          v-model="settings.maxMissingTools"
                          type="number"
                          hide-details
                          hide-spin-buttons
                          :label="$tc('recipe-finder.max-missing-tools')"
                          class="mt-4"
                        />
                      </div>
                      <div class="mt-1">
                        <v-checkbox
                          v-if="isOwnGroup"
                          v-model="settings.includeFoodsOnHand"
                          dense
                          small
                          hide-details
                          class="my-auto"
                          :label="$tc('recipe-finder.include-ingredients-on-hand')"
                        />
                        <v-checkbox
                          v-if="isOwnGroup"
                          v-model="settings.includeToolsOnHand"
                          dense
                          small
                          hide-details
                          class="my-auto"
                          :label="$tc('recipe-finder.include-tools-on-hand')"
                        />
                      </div>
                    </v-card-text>
                  </v-card>
                </v-menu>
              </v-col>
            </v-row>
            <v-row no-gutters class="my-2">
              <v-col cols="12">
                <v-divider />
              </v-col>
            </v-row>
            <v-row no-gutters class="mt-5">
              <v-card-title class="ma-0 pa-0">
                {{ $tc("recipe-finder.selected-ingredients") }}
              </v-card-title>
              <v-container class="ma-0 pa-0" style="max-height: 60vh; overflow-y: auto;">
                <v-card-text v-if="!selectedFoods.length" class="ma-0 pa-0">
                  {{ $tc("recipe-finder.no-ingredients-selected") }}
                </v-card-text>
                <div v-if="useMobile">
                  <v-row no-gutters>
                    <v-col cols="12" class="d-flex flex-wrap justify-end">
                      <v-chip
                        v-for="food in selectedFoods"
                        :key="food.id"
                        label
                        class="ma-1"
                        color="accent custom-transparent"
                        close
                        @click:close="removeFood(food)"
                      >
                        <span class="text-hide-overflow">{{ food.pluralName || food.name }}</span>
                      </v-chip>
                    </v-col>
                  </v-row>
                </div>
                <div v-else>
                  <v-row v-for="food in selectedFoods" :key="food.id" no-gutters class="mb-1">
                    <v-col cols="12">
                      <v-chip
                        label
                        color="accent custom-transparent"
                        close
                        @click:close="removeFood(food)"
                      >
                        <span class="text-hide-overflow">{{ food.pluralName || food.name }}</span>
                      </v-chip>
                    </v-col>
                  </v-row>
                </div>
              </v-container>
            </v-row>
            <v-row v-if="selectedTools.length" no-gutters class="mt-5">
              <v-card-title class="ma-0 pa-0">
                {{ $tc("recipe-finder.selected-tools") }}
              </v-card-title>
              <v-container class="ma-0 pa-0">
                <div v-if="useMobile">
                  <v-row no-gutters>
                    <v-col cols="12" class="d-flex flex-wrap justify-end">
                      <v-chip
                        v-for="tool in selectedTools"
                        :key="tool.id"
                        label
                        class="ma-1"
                        color="accent custom-transparent"
                        close
                        @click:close="removeTool(tool)"
                      >
                        <span class="text-hide-overflow">{{ tool.name }}</span>
                      </v-chip>
                    </v-col>
                  </v-row>
                </div>
                <div v-else>
                  <v-row v-for="tool in selectedTools" :key="tool.id" no-gutters class="mb-1">
                    <v-col cols="12">
                      <v-chip
                        label
                        color="accent custom-transparent"
                        close
                        @click:close="removeTool(tool)"
                      >
                        <span class="text-hide-overflow">{{ tool.name }}</span>
                      </v-chip>
                    </v-col>
                  </v-row>
                </div>
              </v-container>
            </v-row>
          </v-container>
        </v-col>
        <v-col :cols="useMobile ? 12 : 9" :style="useMobile ? '' : 'max-height: 70vh; overflow-y: auto'">
          <v-container
            v-if="recipeSuggestions.readyToMake.length || recipeSuggestions.missingItems.length"
            class="ma-0 pa-0"
          >
            <v-row v-if="recipeSuggestions.readyToMake.length" dense>
              <v-col cols="12">
                <v-card-title :class="attrs.title.class.readyToMake">
                  {{ $tc("recipe-finder.ready-to-make") }}
                </v-card-title>
              </v-col>
              <v-col
                v-for="(item, idx) in recipeSuggestions.readyToMake"
                :key="`${idx}-ready`"
                cols="12"
              >
                <v-lazy>
                  <RecipeSuggestion
                    :recipe="item.recipe"
                    :missing-foods="item.missingFoods"
                    :missing-tools="item.missingTools"
                    :disable-checkbox="loading"
                    @add-food="addFood"
                    @remove-food="removeFood"
                    @add-tool="addTool"
                    @remove-tool="removeTool"
                  />
                </v-lazy>
              </v-col>
            </v-row>
            <v-row v-if="recipeSuggestions.missingItems.length" dense>
              <v-col cols="12">
                <v-card-title :class="attrs.title.class.missingItems">
                  {{ $tc("recipe-finder.almost-ready-to-make") }}
                </v-card-title>
              </v-col>
              <v-col
                v-for="(item, idx) in recipeSuggestions.missingItems"
                :key="`${idx}-missing`"
                cols="12"
              >
              <v-lazy>
                <RecipeSuggestion
                  :recipe="item.recipe"
                  :missing-foods="item.missingFoods"
                  :missing-tools="item.missingTools"
                  :disable-checkbox="loading"
                  @add-food="addFood"
                  @remove-food="removeFood"
                  @add-tool="addTool"
                  @remove-tool="removeTool"
                />
              </v-lazy>
              </v-col>
            </v-row>
          </v-container>
          <v-container v-else-if="!recipesReady">
            <v-row>
              <v-col cols="12" class="d-flex justify-center">
                <div class="text-center">
                  <AppLoader waiting-text="" />
                </div>
              </v-col>
            </v-row>
          </v-container>
          <v-container v-else>
            <v-row>
              <v-col cols="12" class="d-flex flex-row flex-wrap justify-center">
                <v-card-title class="ma-0 pa-0">{{ $tc("recipe-finder.no-recipes-found") }}</v-card-title>
                <v-card-text class="ma-0 pa-0 text-center">
                  {{ $tc("recipe-finder.no-recipes-found-description") }}
                </v-card-text>
              </v-col>
            </v-row>
          </v-container>
        </v-col>
      </v-row>
    </v-container>
    <v-container v-else>
      <v-row>
        <v-col cols="12" class="d-flex justify-center">
          <div class="text-center">
            <AppLoader waiting-text="" />
          </div>
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  onMounted,
  reactive,
  ref,
  toRefs,
  useContext,
  useRoute,
  watch
} from "@nuxtjs/composition-api";
import { watchDebounced } from "@vueuse/core";
import { useUserApi } from "~/composables/api";
import { usePublicExploreApi } from "~/composables/api/api-client";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useFoodStore, usePublicFoodStore, useToolStore, usePublicToolStore } from "~/composables/store";
import { IngredientFood, RecipeSuggestionQuery, RecipeSuggestionResponseItem, RecipeTool } from "~/lib/api/types/recipe";
import { Organizer } from "~/lib/api/types/non-generated";
import QueryFilterBuilder from "~/components/Domain/QueryFilterBuilder.vue";
import RecipeSuggestion from "~/components/Domain/Recipe/RecipeSuggestion.vue";
import SearchFilter from "~/components/Domain/SearchFilter.vue";
import { QueryFilterJSON } from "~/lib/api/types/response";
import { FieldDefinition } from "~/composables/use-query-filter-builder";
import { useRecipeFinderPreferences } from "~/composables/use-users/preferences";

interface RecipeSuggestions {
  readyToMake: RecipeSuggestionResponseItem[];
  missingItems: RecipeSuggestionResponseItem[];
}

export default defineComponent({
  components: { QueryFilterBuilder, RecipeSuggestion, SearchFilter },
  setup() {
    const { $auth, $vuetify, i18n } = useContext();
    const route = useRoute();
    const useMobile = computed(() => $vuetify.breakpoint.smAndDown);

    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");
    const { isOwnGroup } = useLoggedInState();
    const api = isOwnGroup.value ? useUserApi() : usePublicExploreApi(groupSlug.value).explore;

    const preferences = useRecipeFinderPreferences();
    const state = reactive({
      ready: false,
      loading: false,
      recipesReady: false,
      settingsMenu: false,
      queryFilterMenu: false,
      queryFilterMenuKey: 0,
      queryFilterEditorValue: "",
      queryFilterEditorValueJSON: {},
      queryFilterJSON: preferences.value.queryFilterJSON,
      settings: {
        maxMissingFoods: preferences.value.maxMissingFoods,
        maxMissingTools: preferences.value.maxMissingTools,
        includeFoodsOnHand: preferences.value.includeFoodsOnHand,
        includeToolsOnHand: preferences.value.includeToolsOnHand,
        queryFilter: preferences.value.queryFilter,
        limit: 20,
      },
    });

    onMounted(() => {
      if (!isOwnGroup.value) {
        state.settings.includeFoodsOnHand = false;
        state.settings.includeToolsOnHand = false;
      }
    });

    watch(
      () => state,
      (newState) => {
        preferences.value.queryFilter = newState.settings.queryFilter;
        preferences.value.queryFilterJSON = newState.queryFilterJSON;
        preferences.value.maxMissingFoods = newState.settings.maxMissingFoods;
        preferences.value.maxMissingTools = newState.settings.maxMissingTools;
        preferences.value.includeFoodsOnHand = newState.settings.includeFoodsOnHand;
        preferences.value.includeToolsOnHand = newState.settings.includeToolsOnHand;
      },
      {
        deep: true,
      },
    );

    const attrs = computed(() => {
      return {
        title: {
          class: {
            readyToMake: "ma-0 pa-0",
            missingItems: recipeSuggestions.value.readyToMake.length ? "ma-0 pa-0 mt-5" : "ma-0 pa-0",
          },
        },
        searchFilter: {
          colClass: useMobile.value ? "d-flex flex-wrap justify-end" : "d-flex flex-wrap justify-start",
          filterClass: useMobile.value ? "ml-4 mb-2" : "mr-4 mb-2",
        },
        settings: {
          colClass: useMobile.value ? "d-flex flex-wrap justify-end" : "d-flex flex-wrap justify-start",
        },
      };
    })

    const foodStore = isOwnGroup.value ? useFoodStore() : usePublicFoodStore(groupSlug.value);
    const selectedFoods = ref<IngredientFood[]>([]);
    function addFood(food: IngredientFood) {
      selectedFoods.value.push(food);
      handleFoodUpdates();
    }
    function removeFood(food: IngredientFood) {
      selectedFoods.value = selectedFoods.value.filter((f) => f.id !== food.id);
      handleFoodUpdates();
    }
    function handleFoodUpdates() {
      selectedFoods.value.sort((a, b) => (a.pluralName || a.name).localeCompare(b.pluralName || b.name));
      preferences.value.foodIds = selectedFoods.value.map((food) => food.id);
    }
    watch(
      () => selectedFoods.value,
      () => {
        handleFoodUpdates();
      },
    )

    const toolStore = isOwnGroup.value ? useToolStore() : usePublicToolStore(groupSlug.value);
    const selectedTools = ref<RecipeTool[]>([]);
    function addTool(tool: RecipeTool) {
      selectedTools.value.push(tool);
      handleToolUpdates();
    }
    function removeTool(tool: RecipeTool) {
      selectedTools.value = selectedTools.value.filter((t) => t.id !== tool.id);
      handleToolUpdates();
    }
    function handleToolUpdates() {
      selectedTools.value.sort((a, b) => a.name.localeCompare(b.name));
      preferences.value.toolIds = selectedTools.value.map((tool) => tool.id);
    }
    watch(
      () => selectedTools.value,
      () => {
        handleToolUpdates();
      }
    )

    async function hydrateFoods() {
      if (!preferences.value.foodIds.length) {
        return;
      }
      if (!foodStore.store.value.length) {
        await foodStore.actions.refresh();
      }

      const foods = preferences.value.foodIds
      .map((foodId) => foodStore.store.value.find((food) => food.id === foodId))
      .filter((food) => !!food);

      selectedFoods.value = foods;
    }

    async function hydrateTools() {
      if (!preferences.value.toolIds.length) {
        return;
      }
      if (!toolStore.store.value.length) {
        await toolStore.actions.refresh();
      }

      const tools = preferences.value.toolIds
      .map((toolId) => toolStore.store.value.find((tool) => tool.id === toolId))
      .filter((tool) => !!tool);

      selectedTools.value = tools;
    }

    onMounted(async () => {
      await Promise.all([hydrateFoods(), hydrateTools()]);
      state.ready = true;
      if (!selectedFoods.value.length) {
        state.recipesReady = true;
      };
    });

    const recipeResponseItems = ref<RecipeSuggestionResponseItem[]>([]);
    const recipeSuggestions = computed<RecipeSuggestions>(() => {
      const readyToMake: RecipeSuggestionResponseItem[] = [];
      const missingItems: RecipeSuggestionResponseItem[] = [];
      recipeResponseItems.value.forEach((responseItem) => {
        if (responseItem.missingFoods.length === 0 && responseItem.missingTools.length === 0) {
          readyToMake.push(responseItem);
        } else {
          missingItems.push(responseItem);
        };
      });

      return {
        readyToMake,
        missingItems,
      };
    })

    watchDebounced(
      [selectedFoods, selectedTools, state.settings], async () => {
        // don't search for suggestions if no foods are selected
        if(!selectedFoods.value.length) {
          recipeResponseItems.value = [];
          state.recipesReady = true;
          return;
        }

        state.loading = true;
        const { data } = await api.recipes.getSuggestions(
          {
            limit: state.settings.limit,
            queryFilter: state.settings.queryFilter,
            maxMissingFoods: state.settings.maxMissingFoods,
            maxMissingTools: state.settings.maxMissingTools,
            includeFoodsOnHand: state.settings.includeFoodsOnHand,
            includeToolsOnHand: state.settings.includeToolsOnHand,
          } as RecipeSuggestionQuery,
          selectedFoods.value.map((food) => food.id),
          selectedTools.value.map((tool) => tool.id),
        );
        state.loading = false;
        if (!data) {
          return;
        }
        recipeResponseItems.value = data.items;
        state.recipesReady = true;
      },
      {
        debounce: 500,
      },
    );

    const queryFilterBuilderFields: FieldDefinition[] = [
      {
        name: "recipe_category.id",
        label: i18n.tc("category.categories"),
        type: Organizer.Category,
      },
      {
        name: "tags.id",
        label: i18n.tc("tag.tags"),
        type: Organizer.Tag,
      },
      {
        name: "household_id",
        label: i18n.tc("household.households"),
        type: Organizer.Household,
      },
    ];

    function clearQueryFilter() {
      state.queryFilterEditorValue = "";
      state.queryFilterEditorValueJSON = { parts: [] } as QueryFilterJSON;
      state.settings.queryFilter = "";
      state.queryFilterJSON = { parts: [] } as QueryFilterJSON;
      state.queryFilterMenu = false;
      state.queryFilterMenuKey += 1;
    }

    function saveQueryFilter() {
      state.settings.queryFilter = state.queryFilterEditorValue || "";
      state.queryFilterJSON = state.queryFilterEditorValueJSON || { parts: [] } as QueryFilterJSON;
      state.queryFilterMenu = false;
    }

    return {
      ...toRefs(state),
      useMobile,
      attrs,
      isOwnGroup,
      foods: foodStore.store,
      selectedFoods,
      addFood,
      removeFood,
      tools: toolStore.store,
      selectedTools,
      addTool,
      removeTool,
      recipeSuggestions,
      queryFilterBuilderFields,
      clearQueryFilter,
      saveQueryFilter,
    };
  },
  head() {
    return {
      title: this.$tc("recipe-finder.recipe-finder"),
    };
  },
});
</script>
