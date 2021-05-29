<template>
  <v-container>
    <div v-for="(planDay, index) in mealPlan.planDays" :key="index" class="mb-5">
      <v-card-title class="headline">
        {{ $d(new Date(planDay.date), "short") }}
      </v-card-title>
      <v-divider class="mx-2"></v-divider>
      <v-row>
        <v-col cols="12" md="5" sm="12">
          <v-card-title class="headline">Main</v-card-title>
          <RecipeCard
            :name="planDay.meals[0].name"
            :slug="planDay.meals[0].slug"
            :description="planDay.meals[0].description"
          />
        </v-col>
        <v-col cols="12" lg="6" md="6" sm="12">
          <v-card-title class="headline">Sides</v-card-title>
          <MobileRecipeCard
            class="mb-1"
            v-for="(side, index) in planDay.meals.slice(1)"
            :key="`side-${index}`"
            :name="side.name"
            :slug="side.slug"
            :description="side.description"
          />
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script>
import { api } from "@/api";
import { utils } from "@/utils";
import RecipeCard from "@/components/Recipe/RecipeCard";
import MobileRecipeCard from "@/components/Recipe/MobileRecipeCard";
export default {
  components: {
    RecipeCard,
    MobileRecipeCard,
  },
  data() {
    return {
      mealPlan: {},
    };
  },
  async mounted() {
    if (this.mealplanId) {
      this.mealPlan = await api.mealPlans.getById(this.mealplanId);
    } else {
      this.mealPlan = await api.mealPlans.thisWeek();
    }
    if (!this.mealPlan) {
      utils.notify.warning(this.$t("meal-plan.no-meal-plan-defined-yet"));
    }
  },
  computed: {
    mealplanId() {
      return this.$route.query.id || false;
    },
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

<style scoped></style>
