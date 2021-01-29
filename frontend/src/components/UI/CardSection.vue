<template>
  <div class="mt-n5">
    <v-card flat class="transparent" height="60px">
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
            <v-menu offset-y v-if="sortable">
              <template v-slot:activator="{ on, attrs }">
                <v-btn-toggle group>
                  <v-btn text v-bind="attrs" v-on="on"> Sort </v-btn>
                </v-btn-toggle>
              </template>
              <v-list>
                <v-list-item @click="$emit('sort-recent')">
                  <v-list-item-title> Recent </v-list-item-title>
                </v-list-item>
                <v-list-item @click="$emit('sort')">
                  <v-list-item-title> A-Z </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
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
    sortable: {
      default: false,
    },
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