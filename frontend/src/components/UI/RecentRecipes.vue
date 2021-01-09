<template>
  <v-row>
    <v-col
      :sm="6"
      :md="6"
      :lg="4"
      :xl="3"
      v-for="recipe in recipes"
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
</template>

<script>
import RecipeCard from "./RecipeCard";

export default {
  components: {
    RecipeCard,
  },
  data: () => ({}),
  mounted() {},
  computed: {
    recipes() {
      return this.$store.getters.getRecentRecipes;
    },
  },
};
</script>

<style scoped>
</style>
