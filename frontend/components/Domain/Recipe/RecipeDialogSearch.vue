<template>
  <div>
    <slot v-bind="{ open, close }"> </slot>
    <v-dialog v-model="dialog" max-width="988px" content-class="top-dialog" :scrollable="false">
      <v-app-bar sticky dark color="primary lighten-1" :rounded="!$vuetify.breakpoint.xs">
        <v-text-field
          id="arrow-search"
          v-model="search"
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
          placeholder="Search"
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
          <router-link to="/search?advanced=true"> {{ $t("search.advanced-search") }} </router-link>
        </v-card-actions>

        <RecipeCardMobile
          v-for="(recipe, index) in results.slice(0, 10)"
          :key="index"
          :tabindex="index"
          class="ma-1 arrow-nav"
          :name="recipe.name"
          :description="recipe.description || ''"
          :slug="recipe.slug"
          :rating="recipe.rating"
          :image="recipe.image"
          :recipe-id="recipe.id"
          :route="true"
          v-on="$listeners.selected ? { selected: () => handleSelect(recipe) } : {}"
        />
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, toRefs, reactive, ref, watch } from "@nuxtjs/composition-api";
import RecipeCardMobile from "./RecipeCardMobile.vue";
import { useRecipes, allRecipes, useRecipeSearch } from "~/composables/recipes";
import { RecipeSummary } from "~/types/api-types/recipe";
const SELECTED_EVENT = "selected";
export default defineComponent({
  components: {
    RecipeCardMobile,
  },

  setup(_, context) {
    const { refreshRecipes } = useRecipes(true, false);

    const state = reactive({
      loading: false,
      selectedIndex: -1,
      searchResults: [],
    });

    // ===========================================================================
    // Dialong State Management
    const dialog = ref(false);

    // Reset or Grab Recipes on Change
    watch(dialog, async (val) => {
      if (!val) {
        search.value = "";
        state.selectedIndex = -1;
      } else if (allRecipes.value && allRecipes.value.length <= 0) {
        state.loading = true;
        await refreshRecipes();
        state.loading = false;
      }
    });

    function open() {
      dialog.value = true;
    }
    function close() {
      dialog.value = false;
    }

    // ===========================================================================
    // Basic Search

    const { search, results } = useRecipeSearch(allRecipes);
    // ===========================================================================
    // Select Handler

    function handleSelect(recipe: RecipeSummary) {
      close();
      context.emit(SELECTED_EVENT, recipe);
    }

    return { allRecipes, refreshRecipes, ...toRefs(state), dialog, open, close, handleSelect, search, results };
  },
  data() {
    return {};
  },

  computed: {},
  watch: {
    $route() {
      this.dialog = false;
    },
    dialog() {
      if (!this.dialog) {
        document.removeEventListener("keyup", this.onUpDown);
      } else {
        document.addEventListener("keyup", this.onUpDown);
      }
    },
  },
  methods: {
    onUpDown(e: KeyboardEvent) {
      if (e.key === "Enter") {
        console.log(document.activeElement);
        // (document.activeElement as HTMLElement).click();
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        this.selectedIndex--;
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        this.selectedIndex++;
      } else {
        return;
      }
      this.selectRecipe();
    },
    selectRecipe() {
      const recipeCards = document.getElementsByClassName("arrow-nav");
      if (recipeCards) {
        if (this.selectedIndex < 0) {
          this.selectedIndex = -1;
          document.getElementById("arrow-search")?.focus();
          return;
        }

        if (this.selectedIndex >= recipeCards.length) {
          this.selectedIndex = recipeCards.length - 1;
        }

        (recipeCards[this.selectedIndex] as HTMLElement).focus();
      }
    },
  },
});
</script>

<style>
.scroll {
  overflow-y: scroll;
}
</style>