<template>
  <div class="mt-n5" v-if="recipes">
    <v-card flat class="transparent" height="60px">
      <v-card-text>
        <v-row v-if="title != null">
          <v-col>
            <v-btn-toggle group>
              <v-btn text>
                {{ title.toUpperCase() }}
              </v-btn>
            </v-btn-toggle>
          </v-col>
          <v-spacer></v-spacer>
          <v-col align="end">
            <v-menu offset-y v-if="sortable">
              <template v-slot:activator="{ on, attrs }">
                <v-btn-toggle group>
                  <v-btn text v-bind="attrs" v-on="on">
                    {{ $t("general.sort") }}
                  </v-btn>
                </v-btn-toggle>
              </template>
              <v-list>
                <v-list-item @click="$emit('sort-recent')">
                  <v-list-item-title>{{
                    $t("general.recent")
                  }}</v-list-item-title>
                </v-list-item>
                <v-list-item @click="$emit('sort')">
                  <v-list-item-title>{{
                    $t("general.sort-alphabetically")
                  }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    <div v-if="recipes">
      <v-row v-if="!viewScale">
        <v-col
          :sm="6"
          :md="6"
          :lg="4"
          :xl="3"
          v-for="recipe in recipes.slice(0, cardLimit)"
          :key="recipe.name"
        >
          <RecipeCard
            :name="recipe.name"
            :description="recipe.description"
            :slug="recipe.slug"
            :rating="recipe.rating"
            :image="recipe.image"
            :tags="recipe.tags"
          />
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
          <MobileRecipeCard
            :name="recipe.name"
            :description="recipe.description"
            :slug="recipe.slug"
            :rating="recipe.rating"
            :image="recipe.image"
            :tags="recipe.tags"
          />
        </v-col>
      </v-row>
    </div>
    <div v-intersect="bumpList" class="d-flex">
      <v-expand-x-transition>
        <v-progress-circular
          v-if="loading"
          class="mx-auto mt-1"
          :size="50"
          :width="7"
          color="primary"
          indeterminate
        ></v-progress-circular>
      </v-expand-x-transition>
    </div>
  </div>
</template>

<script>
import RecipeCard from "../Recipe/RecipeCard";
import MobileRecipeCard from "@/components/Recipe/MobileRecipeCard";
export default {
  components: {
    RecipeCard,
    MobileRecipeCard,
  },
  props: {
    sortable: {
      default: false,
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
      cardLimit: 30,
      loading: false,
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
  },
  methods: {
    bumpList() {
      const newCardLimit = Math.min(
        this.cardLimit + 20,
        this.effectiveHardLimit
      );

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
  },
};
</script>

<style>
.transparent {
  opacity: 1;
}
</style>