<template>
  <v-container fill-height>
    <v-row justify="center" align="center">
      <v-col sm="12">
        <v-card
          v-for="(meal, index) in mealPlan.meals"
          :key="index"
          class="my-2"
        >
          <v-row dense no-gutters align="center" justify="center">
            <v-col order="1" md="6" sm="12">
              <v-card flat>
                <v-card-title> {{ meal.name }} </v-card-title>
                <v-card-subtitle> {{ meal.dateText }}</v-card-subtitle>

                <v-card-text> {{ meal.description }} </v-card-text>

                <v-card-actions>
                  <v-btn
                    color="secondary"
                    text
                    @click="$router.push(`/recipe/${meal.slug}`)"
                  >
                    View Recipe
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
            <v-col order-sm="0" :order-md="getOrder(index)" md="6" sm="12">
              <v-card>
                <v-img :src="getImage(meal.image)" max-height="300"> </v-img>
              </v-card>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import api from "../../api";
import utils from "../../utils";
export default {
  data() {
    return {
      mealPlan: {},
    };
  },
  async mounted() {
    this.mealPlan = await api.mealPlans.thisWeek();
    console.log(this.mealPlan);
  },
  methods: {
    getOrder(index) {
      if (index % 2 == 0) return 2;
      else return 0;
    },
    getImage(image) {
      return utils.getImageURL(image);
    },
  },
};
</script>

<style scoped>
</style>