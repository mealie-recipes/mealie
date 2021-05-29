<template>
  <div v-if="recipes">
    <v-app-bar color="transparent" flat class="mt-n1 flex-sm-wrap  rounded " v-if="!disableToolbar">
      <v-icon large left v-if="title">
        {{ displayTitleIcon }}
      </v-icon>
      <v-toolbar-title class="headline"> {{ title }} </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn :icon="$vuetify.breakpoint.xsOnly" text @click="navigateRandom">
        <v-icon :left="!$vuetify.breakpoint.xsOnly">
          mdi-dice-multiple
        </v-icon>
        {{ $vuetify.breakpoint.xsOnly ? null : $t("general.random") }}
      </v-btn>
      <v-menu offset-y left v-if="$listeners.sort">
        <template v-slot:activator="{ on, attrs }">
          <v-btn text :icon="$vuetify.breakpoint.xsOnly" v-bind="attrs" v-on="on" :loading="sortLoading">
            <v-icon :left="!$vuetify.breakpoint.xsOnly">
              mdi-sort
            </v-icon>
            {{ $vuetify.breakpoint.xsOnly ? null : $t("general.sort") }}
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="sortRecipes(EVENTS.az)">
            <v-icon left>
              mdi-order-alphabetical-ascending
            </v-icon>
            <v-list-item-title>{{ $t("general.sort-alphabetically") }}</v-list-item-title>
          </v-list-item>
          <v-list-item @click="sortRecipes(EVENTS.rating)">
            <v-icon left>
              mdi-star
            </v-icon>
            <v-list-item-title>{{ $t("general.rating") }}</v-list-item-title>
          </v-list-item>
          <v-list-item @click="sortRecipes(EVENTS.created)">
            <v-icon left>
              mdi-new-box
            </v-icon>
            <v-list-item-title>{{ $t("general.created") }}</v-list-item-title>
          </v-list-item>
          <v-list-item @click="sortRecipes(EVENTS.updated)">
            <v-icon left>
              mdi-update
            </v-icon>
            <v-list-item-title>{{ $t("general.updated") }}</v-list-item-title>
          </v-list-item>
          <v-list-item @click="sortRecipes(EVENTS.shuffle)">
            <v-icon left>
              mdi-shuffle-variant
            </v-icon>
            <v-list-item-title>{{ $t("general.shuffle") }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
    <div v-if="recipes" class="mt-2">
      <v-row v-if="!viewScale">
        <v-col :sm="6" :md="6" :lg="4" :xl="3" v-for="recipe in recipes.slice(0, cardLimit)" :key="recipe.name">
          <v-lazy>
            <RecipeCard
              :name="recipe.name"
              :description="recipe.description"
              :slug="recipe.slug"
              :rating="recipe.rating"
              :image="recipe.image"
              :tags="recipe.tags"
            />
          </v-lazy>
        </v-col>
      </v-row>
      <v-row v-else dense>
        <v-col
          cols="12"
          :sm="singleColumn ? '12' : '12'"
          :md="singleColumn ? '12' : '6'"
          :lg="singleColumn ? '12' : '4'"
          :xl="singleColumn ? '12' : '3'"
          v-for="recipe in recipes.slice(0, cardLimit)"
          :key="recipe.name"
        >
          <v-lazy>
            <MobileRecipeCard
              :name="recipe.name"
              :description="recipe.description"
              :slug="recipe.slug"
              :rating="recipe.rating"
              :image="recipe.image"
              :tags="recipe.tags"
            />
          </v-lazy>
        </v-col>
      </v-row>
    </div>
    <div v-intersect="bumpList" class="d-flex">
      <v-expand-x-transition>
        <SiteLoader v-if="loading" :loading="loading" />
      </v-expand-x-transition>
    </div>
  </div>
</template>

<script>
import SiteLoader from "@/components/UI/SiteLoader";
import RecipeCard from "../Recipe/RecipeCard";
import MobileRecipeCard from "@/components/Recipe/MobileRecipeCard";
import { utils } from "@/utils";
const SORT_EVENT = "sort";

export default {
  components: {
    RecipeCard,
    MobileRecipeCard,
    SiteLoader,
  },
  props: {
    disableToolbar: {
      default: false,
    },
    titleIcon: {
      default: null,
    },
    title: {
      default: null,
    },
    hardLimit: {
      default: 99999,
    },
    mobileCards: {
      default: false,
    },
    singleColumn: {
      defualt: false,
    },
    recipes: Array,
  },
  data() {
    return {
      sortLoading: false,
      cardLimit: 50,
      loading: false,
      EVENTS: {
        az: "az",
        rating: "rating",
        created: "created",
        updated: "updated",
        shuffle: "shuffle",
      },
    };
  },
  watch: {
    recipes() {
      this.bumpList();
    },
  },
  computed: {
    viewScale() {
      if (this.mobileCards) return true;
      switch (this.$vuetify.breakpoint.name) {
        case "xs":
          return true;
        case "sm":
          return true;
        default:
          return false;
      }
    },
    effectiveHardLimit() {
      return Math.min(this.hardLimit, this.recipes.length);
    },
    displayTitleIcon() {
      return this.titleIcon || this.$globals.icons.tags;
    },
  },
  methods: {
    bumpList() {
      const newCardLimit = Math.min(this.cardLimit + 20, this.effectiveHardLimit);

      if (this.loading === false && newCardLimit > this.cardLimit) {
        this.setLoader();
      }

      this.cardLimit = newCardLimit;
    },
    async setLoader() {
      this.loading = true;
      await new Promise(r => setTimeout(r, 1000));
      this.loading = false;
    },
    navigateRandom() {
      const recipe = utils.recipe.randomRecipe(this.recipes);
      this.$router.push(`/recipe/${recipe.slug}`);
    },
    sortRecipes(sortType) {
      this.sortLoading = true;
      let sortTarget = [...this.recipes];
      switch (sortType) {
        case this.EVENTS.az:
          utils.recipe.sortAToZ(sortTarget);
          break;
        case this.EVENTS.rating:
          utils.recipe.sortByRating(sortTarget);
          break;
        case this.EVENTS.created:
          utils.recipe.sortByCreated(sortTarget);
          break;
        case this.EVENTS.updated:
          utils.recipe.sortByUpdated(sortTarget);
          break;
        case this.EVENTS.shuffle:
          utils.recipe.shuffle(sortTarget);
          break;
        default:
          console.log("Unknown Event", sortType);
          return;
      }

      this.$emit(SORT_EVENT, sortTarget);
      this.sortLoading = false;
    },
  },
};
</script>

<style>
.transparent {
  opacity: 1;
}
</style>
