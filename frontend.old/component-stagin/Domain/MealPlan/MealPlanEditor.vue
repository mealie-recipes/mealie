<template>
  <v-card>
    <v-card-title class="headline">
      {{ $t("meal-plan.edit-meal-plan") }}
    </v-card-title>
    <v-divider></v-divider>

    <v-card-text>
      <MealPlanCard v-model="mealPlan.planDays" />
      <v-row align="center" justify="end">
        <v-card-actions>
          <TheButton update @click="update" />
          <v-spacer></v-spacer>
        </v-card-actions>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { api } from "@/api";
import { utils } from "@/utils";
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
      const dateObject = new Date(timestamp);
      return utils.getDateAsPythonDate(dateObject);
    },
    async update() {
      if (await api.mealPlans.update(this.mealPlan.uid, this.mealPlan)) {
        this.$emit("updated");
      }
    },
  },
};
</script>

<style></style>
