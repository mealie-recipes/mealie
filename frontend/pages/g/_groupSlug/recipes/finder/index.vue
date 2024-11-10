<template>
  <v-container>
    <v-container>
      <v-row>
        <v-col cols="3">
          <v-container class="ma-0 pa-0">
            <v-row no-gutters>
              <v-col cols="12" no-gutters class="d-flex flex-wrap justify-start">
                <SearchFilter v-if="foods" v-model="selectedFoods" :items="foods" class="mr-6 mb-2">
                  <v-icon left>
                    {{ $globals.icons.foods }}
                  </v-icon>
                  {{ $t("general.foods") }}
                </SearchFilter>
                <SearchFilter v-if="tools" v-model="selectedTools" :items="tools" class="mr-6 mb-2">
                  <v-icon left>
                    {{ $globals.icons.potSteam }}
                  </v-icon>
                  {{ $t("tool.tools") }}
                </SearchFilter>
                <v-btn
                  small
                  color="accent"
                  dark
                  @click="queryFilterMenu = !queryFilterMenu"
                  class="mr-6 mb-2"
                >
                  <v-icon left>
                    {{ $globals.icons.filter }}
                  </v-icon>
                  Other Filters
                  <BaseDialog
                    v-model="queryFilterMenu"
                    title="Other Filters"
                    :icon="$globals.icons.filter"
                  >
                    <!-- <QueryFilterBuilder /> -->
                  </BaseDialog>
                </v-btn>
              </v-col>
            </v-row>
            <!-- Settings Menu -->
            <v-row no-gutters class="mb-2">
              <v-col cols="12">
                <v-menu
                  v-model="settingsMenu"
                  offset-y
                  nudge-bottom="3"
                  :close-on-content-click="false"
                >
                  <template #activator="{ on, attrs }">
                    <v-btn small color="primary" dark v-bind="attrs" v-on="on">
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
                          label="Max Missing Foods"
                        />
                        <v-text-field
                          v-model="settings.maxMissingTools"
                          type="number"
                          hide-details
                          hide-spin-buttons
                          label="Max Missing Tools"
                          class="mt-4"
                        />
                      </div>
                      <div class="mt-1">
                        <v-checkbox
                          v-model="settings.includeFoodsOnHand"
                          dense
                          small
                          hide-details
                          class="my-auto"
                          label="Include Foods On Hand"
                        />
                        <v-checkbox
                          v-model="settings.includeToolsOnHand"
                          dense
                          small
                          hide-details
                          class="my-auto"
                          label="Include Tools On Hand"
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
                Selected Foods
              </v-card-title>
              <v-container class="ma-0 pa-0" style="max-height: 60vh; overflow-y: auto;">
                <v-card-text v-if="!selectedFoods.length" class="ma-0 pa-0">
                  No foods selected
                </v-card-text>
                <v-row v-for="food in selectedFoods" :key="food.id" no-gutters class="mb-1">
                  <v-col cols="12">
                    <v-chip
                      label
                      color="accent custom-transparent"
                      close
                      @click:close="removeFood(food)"
                    >
                      <span class="text-hide-overflow">{{ food.name }}</span>
                    </v-chip>
                  </v-col>
                </v-row>
              </v-container>
            </v-row>
            <v-row v-if="selectedTools.length" no-gutters class="mt-5">
              <v-card-title class="ma-0 pa-0">
                Selected Tools
              </v-card-title>
              <v-container class="ma-0 pa-0">
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
              </v-container>
            </v-row>
          </v-container>
        </v-col>
        <v-col cols="9">
          <v-container
            class="ma-0 pa-0"
            v-if="recipeSuggestions.readyToMake.length || recipeSuggestions.missingItems.length"
          >
            <v-row v-if="recipeSuggestions.readyToMake.length" dense>
              <v-col cols="12">
                <v-card-title :class="attrs.class.title.readyToMake">
                  Ready to Make
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
                    :missingFoods="item.missingFoods"
                    :missingTools="item.missingTools"
                  />
                </v-lazy>
              </v-col>
            </v-row>
            <v-row v-if="recipeSuggestions.missingItems.length" dense>
              <v-col cols="12">
                <v-card-title :class="attrs.class.title.missingItems">
                  Almost Ready to Make
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
                  :missingFoods="item.missingFoods"
                  :missingTools="item.missingTools"
                />
              </v-lazy>
              </v-col>
            </v-row>
          </v-container>
          <v-container v-else>
            <v-row>
              <v-col cols="12" class="d-flex flex-row flex-wrap justify-center">
                <v-card-title class="ma-0 pa-0">No recipes found</v-card-title>
                <v-card-text class="ma-0 pa-0 text-center">
                  Try adding more foods to your search or adjusting your filters
                </v-card-text>
              </v-col>
            </v-row>
          </v-container>
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, toRefs, reactive, ref, useContext, useRoute, watch } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { usePublicExploreApi } from "~/composables/api/api-client";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useFoodStore, usePublicFoodStore, useToolStore, usePublicToolStore } from "~/composables/store";
import { IngredientFood, RecipeTool } from "~/lib/api/types/recipe";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import QueryFilterBuilder from "~/components/Domain/QueryFilterBuilder.vue";
import RecipeSuggestion from "~/components/Domain/Recipe/RecipeSuggestion.vue";
import SearchFilter from "~/components/Domain/SearchFilter.vue";
import { RecipeSuggestionQuery, RecipeSuggestionResponseItem } from "~/lib/api/types/response";
import { watchDebounced } from "@vueuse/core";

interface RecipeSuggestions {
  readyToMake: RecipeSuggestionResponseItem[];
  missingItems: RecipeSuggestionResponseItem[];
}

export default defineComponent({
  components: { QueryFilterBuilder, RecipeSuggestion, SearchFilter },
  setup() {
    const state = reactive({
      settingsMenu: false,
      queryFilterMenu: false,
      settings: {
        maxMissingFoods: 5,
        maxMissingTools: 5,
        includeFoodsOnHand: true,
        includeToolsOnHand: true,
        queryFilter: "",
      },
    });

    const { $auth } = useContext();
    const route = useRoute();

    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");
    const { isOwnGroup } = useLoggedInState();
    const api = isOwnGroup.value ? useUserApi() : usePublicExploreApi(groupSlug.value).explore;

    const attrs = computed(() => {
      return {
        class: {
          title: {
            readyToMake: "ma-0 pa-0",
            missingItems: recipeSuggestions.value.readyToMake.length ? "ma-0 pa-0 mt-5" : "ma-0 pa-0",
          }
        }
      }
    })

    const foodStore = isOwnGroup.value ? useFoodStore() : usePublicFoodStore(groupSlug.value);
    const selectedFoods = ref<IngredientFood[]>([]);
    function removeFood(food: IngredientFood) {
      selectedFoods.value = selectedFoods.value.filter((f) => f.id !== food.id);
    }
    watch(
      () => selectedFoods.value,
      () => {
        selectedFoods.value.sort((a, b) => a.name.localeCompare(b.name));
      }
    )

    const toolStore = isOwnGroup.value ? useToolStore() : usePublicToolStore(groupSlug.value);
    const selectedTools = ref<NoUndefinedField<RecipeTool>[]>([]);
    function removeTool(tool: NoUndefinedField<RecipeTool>) {
      selectedTools.value = selectedTools.value.filter((t) => t.id !== tool.id);
    }
    watch(
      () => selectedTools.value,
      () => {
        selectedTools.value.sort((a, b) => a.name.localeCompare(b.name));
      }
    )

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
          return;
        }

        const { data } = await api.recipes.getSuggestions(
          {
            limit: 10,
            queryFilter: state.settings.queryFilter,
            maxMissingFoods: state.settings.maxMissingFoods,
            maxMissingTools: state.settings.maxMissingTools,
            includeFoodsOnHand: state.settings.includeFoodsOnHand,
            includeToolsOnHand: state.settings.includeToolsOnHand,
          } as RecipeSuggestionQuery,
          selectedFoods.value.map((food) => food.id),
          selectedTools.value.map((tool) => tool.id),
        );
        if (!data) {
          return;
        }
        recipeResponseItems.value = data.items;
      },
      {
        debounce: 1000,
      },
    );

    return {
      ...toRefs(state),
      attrs,
      foods: foodStore.store,
      selectedFoods,
      removeFood,
      tools: toolStore.store,
      selectedTools,
      removeTool,
      recipeSuggestions,
    };
  },
  head() {
    return {
      title: this.$tc("recipe-finder.recipe-finder"),
    };
  },
});
</script>
