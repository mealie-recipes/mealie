<template>
  <v-container>
    <v-container>
      <v-row>
        <v-col cols="2">
          <v-container class="ma-0 pa-0">
            <v-row no-gutters class="mb-5">
              <v-col cols="6" no-gutters>
                <SearchFilter v-if="foods" v-model="selectedFoods" :items="foods">
                  <v-icon left>
                    {{ $globals.icons.foods }}
                  </v-icon>
                  {{ $t("general.foods") }}
                </SearchFilter>
              </v-col>
              <v-col cols="6" no-gutters>
                <SearchFilter v-if="tools" v-model="selectedTools" :items="tools">
                  <v-icon left>
                    {{ $globals.icons.potSteam }}
                  </v-icon>
                  {{ $t("tool.tools") }}
                </SearchFilter>
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-card-title class="ma-0 pa-0">
                Selected Foods
              </v-card-title>
              <v-container no-gutters>
                <v-card-text v-if="!selectedFoods.length" class="ma-0 pa-0">
                  No foods selected
                </v-card-text>
                <v-row v-for="food in selectedFoods" :key="food.id" no-gutters class="mb-1">
                  <v-col no-gutters cols="12">
                    <v-chip
                      label
                      color="accent custom-transparent"
                      close
                      @click:close="removeFood(food)"
                    >
                      <span>{{ food.name }}</span>
                    </v-chip>
                  </v-col>
                </v-row>
              </v-container>
            </v-row>
          </v-container>
        </v-col>
        <v-col cols="10">
          <v-container class="ma-0 pa-0">
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
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useContext, useRoute } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { usePublicExploreApi } from "~/composables/api/api-client";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useFoodStore, usePublicFoodStore, useToolStore, usePublicToolStore } from "~/composables/store";
import { IngredientFood, RecipeTool } from "~/lib/api/types/recipe";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import RecipeSuggestion from "~/components/Domain/Recipe/RecipeSuggestion.vue";
import SearchFilter from "~/components/Domain/SearchFilter.vue";
import { RecipeSuggestionQuery, RecipeSuggestionResponseItem } from "~/lib/api/types/response";
import { watchDebounced } from "@vueuse/core";

interface RecipeSuggestions {
  readyToMake: RecipeSuggestionResponseItem[];
  missingItems: RecipeSuggestionResponseItem[];
}

export default defineComponent({
  components: { RecipeSuggestion, SearchFilter },
  setup() {
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

    const toolStore = isOwnGroup.value ? useToolStore() : usePublicToolStore(groupSlug.value);
    const selectedTools = ref<NoUndefinedField<RecipeTool>[]>([]);
    function removeTool(tool: NoUndefinedField<RecipeTool>) {
      selectedTools.value = selectedTools.value.filter((t) => t.id !== tool.id);
    }

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



    watchDebounced([selectedFoods, selectedTools], async () => {
      if(!selectedFoods.value.length && !selectedTools.value.length) {
        recipeResponseItems.value = [];
        return;
      }
      console.log(selectedFoods.value);

      const { data } = await api.recipes.getSuggestions(
        {
          limit: 10,
          maxMissingFoods: 5,
          maxMissingTools: 5,
          includeFoodsOnHand: true,
          includeToolsOnHand: true,
        } as RecipeSuggestionQuery,
        selectedFoods.value.map((food) => food.id),
        selectedTools.value.map((tool) => tool.id),
      );
      if (!data) {
        return;
      }
      recipeResponseItems.value = data.items;
    });

    return {
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
