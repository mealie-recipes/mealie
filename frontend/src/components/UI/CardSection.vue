<template>
  <div class="mt-n5">
    <v-card flat class="transparent mb-2" height="50px">
      <v-card-text>
        <v-row>
          <v-col>
            <v-btn-toggle group>
              <v-btn text :to="`/recipes/category/${title.toLowerCase()}`">
                {{ title.toUpperCase() }}
              </v-btn>
            </v-btn-toggle>
          </v-col>
          <v-spacer></v-spacer>
          <v-col align="end">
            <v-btn-toggle group>
              <v-btn text color="accent"> Sort </v-btn>
              <v-btn text color="accent"> Limit </v-btn>
            </v-btn-toggle>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    <v-row>
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
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import RecipeCard from "./RecipeCard";
export default {
  components: {
    RecipeCard,
  },
  props: {
    title: String,
    recipes: Array,
    cardLimit: {
      default: 6,
    },
  },
  data() {
    return {};
  },
};
</script>

<style>
.transparent {
  opacity: 1;
}
</style>