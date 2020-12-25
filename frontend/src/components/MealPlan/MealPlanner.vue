<template>
  <div>
    <EditPlan
      v-if="editMealPlan"
      :meal-plan="editMealPlan"
      @updated="planUpdated"
    />
    <NewMeal v-else @created="requestMeals" />

    <v-card class="my-1">
      <v-card-title class="accent white--text"> Meal Plans </v-card-title>

      <v-timeline align-top :dense="$vuetify.breakpoint.smAndDown">
        <v-timeline-item
          class="px-1"
          v-for="(mealplan, i) in plannedMeals"
          :key="i"
          color="accent lighten-2"
          icon="mdi-silverware-variant"
          fill-dot
        >
          <v-card color="accent lighten-2" dark>
            <v-card-title class="title">
              {{ formatDate(mealplan.startDate) }} -
              {{ formatDate(mealplan.endDate) }}
            </v-card-title>

            <v-card-text class="white text--primary">
              <v-row dense align="center">
                <v-col></v-col>
                <v-col
                  v-for="(meal, index) in mealplan.meals"
                  :key="generateKey(meal.slug, index)"
                >
                  <v-img
                    class="rounded-lg"
                    :src="getImage(meal.image)"
                    height="80"
                    width="80"
                  >
                  </v-img>
                </v-col>
                <v-col></v-col>
              </v-row>
              <v-btn
                color="accent lighten-2"
                class="mx-0"
                outlined
                @click="editPlan(mealplan.uid)"
              >
                Edit
              </v-btn>
              <v-btn
                color="error lighten-2"
                class="mx-2"
                outlined
                @click="deletePlan(mealplan.uid)"
              >
                Delete
              </v-btn>
            </v-card-text>
          </v-card>
        </v-timeline-item>
      </v-timeline>
    </v-card>
  </div>
</template>

<script>
import api from "../../api";
import utils from "../../utils";
import NewMeal from "./NewMeal";
import EditPlan from "./EditPlan";

export default {
  components: {
    NewMeal,
    EditPlan,
  },
  data: () => ({
    plannedMeals: [],
    editMealPlan: null,
  }),
  async mounted() {
    this.requestMeals();
  },
  methods: {
    async requestMeals() {
      const response = await api.mealPlans.all();
      this.plannedMeals = response.data;
    },
    generateKey(name, index) {
      return utils.generateUniqueKey(name, index);
    },
    formatDate(timestamp) {
      let dateObject = new Date(timestamp);
      return utils.getDateAsTextAlt(dateObject);
    },
    getImage(image) {
      return utils.getImageURL(image);
    },

    editPlan(id) {
      this.plannedMeals.forEach((element) => {
        if (element.uid === id) {
          console.log(element);
          this.editMealPlan = element;
        }
      });
    },
    planUpdated() {
      this.editMealPlan = null;
      this.requestMeals();
    },
    deletePlan(id) {
      api.mealPlans.delete(id);
      this.requestMeals();
    },
  },
};
</script>

<style>
</style>