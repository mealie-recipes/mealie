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
          sm="12"
          md="6"
          lg="4"
          xl="3"
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
      <v-progress-circular
        v-if="loading"
        class="mx-auto mt-1"
        :size="50"
        :width="7"
        color="primary"
        indeterminate
      ></v-progress-circular>
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
    recipes: Array,
  },
  data() {
    return {
      cardLimit: 30,
      loading: false,
    };
  },
  computed: {
    viewScale() {
      switch (this.$vuetify.breakpoint.name) {
        case "xs":
          return true;
        case "sm":
          return true;
        default:
          return false;
      }
    },
  },
  methods: {
    bumpList() {
      const newCardLimit = Math.min(this.cardLimit + 20, this.hardLimit);

      if (this.loading === false && newCardLimit > this.cardLimit) {
        this.setLoader();
      }

      this.cardLimit = newCardLimit;
    },
    async setLoader() {
      this.loading = true;
      await new Promise(r => setTimeout(r, 3000));
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