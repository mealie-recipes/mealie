<template>
  <div>
    <slot v-bind="{ open, close }"> </slot>
    <v-dialog
      v-model="dialog"
      :width="isMobile ? undefined : '65%'"
      :height="isMobile ? undefined : '0'"
      :fullscreen="isMobile"
      content-class="top-dialog"
      :scrollable="false"
    >
      <v-app-bar sticky dark color="primary lighten-1" :rounded="!isMobile">
        <FuseSearchBar :raw-data="allItems" @results="filterItems" :search="searchString">
          <v-text-field
            id="arrow-search"
            autofocus
            v-model="searchString"
            solo
            flat
            autocomplete="off"
            background-color="primary lighten-1"
            color="white"
            dense
            :clearable="!isMobile"
            class="mx-2 arrow-search"
            hide-details
            single-line
            :placeholder="$t('search.search')"
            :prepend-inner-icon="$globals.icons.search"
          >
          </v-text-field>
        </FuseSearchBar>
        <v-btn v-if="isMobile" x-small fab light @click="dialog = false">
          <v-icon>
            {{ $globals.icons.close }}
          </v-icon>
        </v-btn>
      </v-app-bar>
      <v-card class="mt-1 pa-1" relative>
        <v-card-actions>
          <div class="mr-auto">
            {{ $t("search.results") }}
          </div>
          <router-link to="/search"> {{ $t("search.advanced-search") }} </router-link>
        </v-card-actions>
        <v-card-actions v-if="loading">
          <SiteLoader :loading="loading" />
        </v-card-actions>
        <div v-else>
          <MobileRecipeCard
            v-for="(recipe, index) in results.slice(0, 10)"
            :tabindex="index"
            :key="index"
            class="ma-1 arrow-nav"
            :name="recipe.name"
            :description="recipe.description"
            :slug="recipe.slug"
            :rating="recipe.rating"
            :image="recipe.image"
            :route="true"
            v-on="$listeners.selected ? { selected: () => grabRecipe(recipe) } : {}"
          />
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import SiteLoader from "@/components/UI/SiteLoader";
const SELECTED_EVENT = "selected";
import FuseSearchBar from "@/components/UI/Search/FuseSearchBar";
import MobileRecipeCard from "@/components/Recipe/MobileRecipeCard";
export default {
  components: {
    FuseSearchBar,
    MobileRecipeCard,
    SiteLoader,
  },
  data() {
    return {
      loading: false,
      selectedIndex: -1,
      dialog: false,
      searchString: "",
      searchResults: [],
    };
  },
  watch: {
    $route() {
      this.dialog = false;
    },
    async dialog(val) {
      if (!val) {
        this.resetSelected();
      } else if (this.allItems.length <= 0) {
        this.loading = true;
        await this.$store.dispatch("requestAllRecipes");
        this.loading = false;
      }
    },
  },
  mounted() {
    document.addEventListener("keydown", this.onUpDown);
  },
  beforeDestroy() {
    document.removeEventListener("keydown", this.onUpDown);
  },

  computed: {
    isMobile() {
      return this.$vuetify.breakpoint.name === "xs";
    },
    allItems() {
      return this.$store.getters.getAllRecipes;
    },
    results() {
      if (this.searchString != null && this.searchString.length >= 1) {
        return this.searchResults;
      }
      return this.allItems;
    },
  },
  methods: {
    open() {
      this.dialog = true;
    },
    close() {
      this.dialog = false;
    },
    filterItems(val) {
      this.searchResults = val.map(x => x.item);
    },
    grabRecipe(recipe) {
      this.dialog = false;
      this.$emit(SELECTED_EVENT, recipe);
    },
    onUpDown(e) {
      if (this.dialog) {
        if (e.keyCode === 38) {
          e.preventDefault();
          this.selectedIndex--;
        } else if (e.keyCode === 40) {
          e.preventDefault();
          this.selectedIndex++;
        } else {
          return;
        }
        this.selectRecipe();
      }
    },
    resetSelected() {
      this.searchString = "";
      this.selectedIndex = -1;
      document.getElementsByClassName("arrow-nav")[0].focus();
    },
    selectRecipe() {
      const recipeCards = document.getElementsByClassName("arrow-nav");
      if (recipeCards) {
        if (this.selectedIndex < 0) {
          this.selectedIndex = -1;
          document.getElementById("arrow-search").focus();
          return;
        }
        this.selectedIndex >= recipeCards.length ? (this.selectedIndex = recipeCards.length - 1) : null;
        recipeCards[this.selectedIndex].focus();
      }
    },
  },
};
</script>

<style >
</style>
