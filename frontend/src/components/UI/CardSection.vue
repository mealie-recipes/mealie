<template>
  <div class="mt-n5" v-if="recipes">
    <v-card flat class="transparent" height="60px">
      <v-card-text>
        <v-row v-if="title != null">
          <v-col>
            <v-btn-toggle group>
              <v-btn text :to="`/recipes/${title.toLowerCase()}`">
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
          />
        </v-col>
      </v-row>
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
    recipes: Array,
    cardLimit: {
      default: 999,
    },
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
};
</script>

<style>
.transparent {
  opacity: 1;
}
</style>