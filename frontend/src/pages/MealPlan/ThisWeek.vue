<template>
  <v-container fill-height>
    <v-row>
      <v-col sm="12">
        <v-card
          v-for="(meal, index) in mealPlan.meals"
          :key="index"
          class="my-2"
        >
          <v-row dense no-gutters align="center" justify="center">
            <v-col order="1" md="6" sm="12">
              <v-card
                flat
                class="align-center justify-center"
                align="center"
                justify="center"
              >
                <v-card-title class="justify-center">
                  {{ meal.name }}
                </v-card-title>
                <v-card-subtitle>
                  {{ $d(new Date(meal.date), "short") }}</v-card-subtitle
                >

                <v-card-text> {{ meal.description }} </v-card-text>

                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn
                    align="center"
                    color="secondary"
                    text
                    @click="$router.push(`/recipe/${meal.slug}`)"
                  >
                    {{ $t("recipe.view-recipe") }}
                  </v-btn>
                  <v-spacer></v-spacer>
                </v-card-actions>
              </v-card>
            </v-col>
            <v-col order-sm="0" :order-md="getOrder(index)" md="6" sm="12">
              <v-card flat>
                <v-img :src="getImage(meal.slug)" max-height="300"> </v-img>
              </v-card>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { api } from "@/api";
export default {
  data() {
    return {
      mealPlan: {},
    };
  },
  async mounted() {
    this.mealPlan = await api.mealPlans.thisWeek();
  },
  methods: {
    getOrder(index) {
      if (index % 2 == 0) return 2;
      else return 0;
    },
    getImage(image) {
      return api.recipes.recipeImage(image);
    },
  },
};
</script>

<style scoped>
</style>