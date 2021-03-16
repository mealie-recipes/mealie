<template>
  <v-container>
    <EditPlan
      v-if="editMealPlan"
      :meal-plan="editMealPlan"
      @updated="planUpdated"
    />
    <NewMeal v-else @created="requestMeals" class="mb-5" />
    <ShoppingListDialog ref="shoppingList" />

    <v-card class="my-2">
      <v-card-title class="headline">
        {{ $t("meal-plan.meal-plans") }}
      </v-card-title>
      <v-divider></v-divider>
    </v-card>
    <v-row dense>
      <v-col
        :sm="6"
        :md="6"
        :lg="4"
        :xl="3"
        v-for="(mealplan, i) in plannedMeals"
        :key="i"
      >
        <v-card class="mt-1">
          <v-card-title>
            {{ $d(new Date(mealplan.startDate.split("-")), "short") }} -
            {{ $d(new Date(mealplan.endDate.split("-")), "short") }}
          </v-card-title>
          <v-list nav>
            <v-list-item-group color="primary">
              <v-list-item
                v-for="(meal, index) in mealplan.meals"
                :key="generateKey(meal.slug, index)"
                :to="meal.slug ? `/recipe/${meal.slug}` : null"
              >
                <v-list-item-avatar
                  color="primary"
                  class="headline font-weight-light white--text"
                >
                  <v-img :src="getImage(meal.image)"></v-img>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title v-text="meal.name"></v-list-item-title>
                  <v-list-item-subtitle
                    v-text="$d(new Date(meal.date.split('-')), 'short')"
                  >
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list-item-group>
          </v-list>
          <v-card-actions class="mt-n5">
            <v-btn
              color="accent lighten-2"
              class="mx-0"
              text
              @click="openShoppingList(mealplan.uid)"
            >
              {{ $t("meal-plan.shopping-list") }}
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn
              color="accent lighten-2"
              class="mx-0"
              text
              @click="editPlan(mealplan.uid)"
            >
              {{ $t("general.edit") }}
            </v-btn>
            <v-btn
              color="error lighten-2"
              class="mx-2"
              text
              @click="deletePlan(mealplan.uid)"
            >
              {{ $t("general.delete") }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import api from "@/api";
import utils from "@/utils";
import NewMeal from "@/components/MealPlan/MealPlanNew";
import EditPlan from "@/components/MealPlan/MealPlanEditor";
import ShoppingListDialog from "@/components/MealPlan/ShoppingListDialog";

export default {
  components: {
    NewMeal,
    EditPlan,
    ShoppingListDialog,
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
      this.plannedMeals.forEach(element => {
        if (element.uid === id) {
          this.editMealPlan = element;
        }
      });
    },
    planUpdated() {
      this.editMealPlan = null;
      this.requestMeals();
    },
    async deletePlan(id) {
      await api.mealPlans.delete(id);
      this.requestMeals();
    },
    openShoppingList(id) {
      this.$refs.shoppingList.openDialog(id);
    },
  },
};
</script>

<style>
</style>