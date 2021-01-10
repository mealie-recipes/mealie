<template>
  <v-card>
    <v-card-title class="headline"> Edit Meal Plan </v-card-title>
    <v-divider></v-divider>
    <v-card-text>
      <MealPlanCard v-model="mealPlan.meals" />
      <v-row align="center" justify="end">
        <v-card-actions>
          <v-btn color="success" text @click="update"> Update </v-btn>
          <v-spacer></v-spacer>
        </v-card-actions>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import api from "../../api";
import utils from "../../utils";
import MealPlanCard from "./MealPlanCard";
export default {
  components: {
    MealPlanCard,
  },
  props: {
    mealPlan: Object,
  },
  methods: {
    formatDate(timestamp) {
      let dateObject = new Date(timestamp);
      return utils.getDateAsPythonDate(dateObject);
    },
    async update() {
      await api.mealPlans.update(this.mealPlan.uid, this.mealPlan);
      this.$emit("updated");
    },
  },
};
</script>

<style>
</style>