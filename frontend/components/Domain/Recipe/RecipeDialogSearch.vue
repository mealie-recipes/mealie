<template>
  <div>
    <slot v-bind="{ open, close }"> </slot>
    <v-dialog v-model="dialog" max-width="988px" content-class="top-dialog" :scrollable="false">
      <v-app-bar sticky dark color="primary lighten-1" :rounded="!$vuetify.breakpoint.xs">
        <v-text-field
          id="arrow-search"
          v-model="search.query.value"
          autofocus
          solo
          flat
          autocomplete="off"
          background-color="primary lighten-1"
          color="white"
          dense
          class="mx-2 arrow-search"
          hide-details
          single-line
          :placeholder="$t('search.search')"
          :prepend-inner-icon="$globals.icons.search"
        ></v-text-field>

        <v-btn v-if="$vuetify.breakpoint.xs" x-small fab light @click="dialog = false">
          <v-icon>
            {{ $globals.icons.close }}
          </v-icon>
        </v-btn>
      </v-app-bar>
      <v-card class="mt-1 pa-1 scroll" max-height="700px" relative :loading="loading">
        <v-card-actions>
          <div class="mr-auto">
            {{ $t("search.results") }}
          </div>
          <router-link :to="advancedSearchUrl"> {{ $t("search.advanced-search") }} </router-link>
        </v-card-actions>

        <RecipeCardMobile
          v-for="(recipe, index) in search.data.value"
          :key="index"
          :tabindex="index"
          class="ma-1 arrow-nav"
          :name="recipe.name"
          :description="recipe.description || ''"
          :slug="recipe.slug"
          :rating="recipe.rating"
          :image="recipe.image"
          :recipe-id="recipe.id"
          v-on="$listeners.selected ? { selected: () => handleSelect(recipe) } : {}"
        />
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, toRefs, reactive, ref, watch, useContext, useRoute } from "@nuxtjs/composition-api";
import RecipeCardMobile from "./RecipeCardMobile.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { RecipeSummary } from "~/lib/api/types/recipe";
import { useUserApi } from "~/composables/api";
import { useRecipeSearch } from "~/composables/recipes/use-recipe-search";
import { usePublicExploreApi } from "~/composables/api/api-client";
const SELECTED_EVENT = "selected";
export default defineComponent({
  components: {
    RecipeCardMobile,
  },

  setup(_, context) {
    const { $auth } = useContext();
    const state = reactive({
      loading: false,
      selectedIndex: -1,
    });

    // ===========================================================================
    // Dialog State Management
    const dialog = ref(false);

    // Reset or Grab Recipes on Change
    watch(dialog, (val) => {
      if (!val) {
        search.query.value = "";
        state.selectedIndex = -1;
        search.data.value = [];
      }
    });

    // ===========================================================================
    // Event Handlers

    function selectRecipe() {
      const recipeCards = document.getElementsByClassName("arrow-nav");
      if (recipeCards) {
        if (state.selectedIndex < 0) {
          state.selectedIndex = -1;
          document.getElementById("arrow-search")?.focus();
          return;
        }

        if (state.selectedIndex >= recipeCards.length) {
          state.selectedIndex = recipeCards.length - 1;
        }

        (recipeCards[state.selectedIndex] as HTMLElement).focus();
      }
    }

    function onUpDown(e: KeyboardEvent) {
      if (e.key === "Enter") {
        console.log(document.activeElement);
        // (document.activeElement as HTMLElement).click();
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        state.selectedIndex--;
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        state.selectedIndex++;
      } else {
        return;
      }
      selectRecipe();
    }

    watch(dialog, (val) => {
      if (!val) {
        document.removeEventListener("keyup", onUpDown);
      } else {
        document.addEventListener("keyup", onUpDown);
      }
    });

    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");
    const route = useRoute();
    const advancedSearchUrl = computed(() => `/g/${groupSlug.value}`)
    watch(route, close);

    function open() {
      dialog.value = true;
    }
    function close() {
      dialog.value = false;
    }

    // ===========================================================================
    // Basic Search
    const { isOwnGroup } = useLoggedInState();
    const api = isOwnGroup.value ? useUserApi() : usePublicExploreApi(groupSlug.value).explore;
    const search = useRecipeSearch(api);

    // Select Handler

    function handleSelect(recipe: RecipeSummary) {
      close();
      context.emit(SELECTED_EVENT, recipe);
    }

    return {
      ...toRefs(state),
      advancedSearchUrl,
      dialog,
      open,
      close,
      handleSelect,
      search,
    };
  },
});
</script>

<style>
.scroll {
  overflow-y: auto;
}
</style>
