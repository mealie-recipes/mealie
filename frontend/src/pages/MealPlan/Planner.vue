<template>
  <v-container>
    <EditPlan v-if="editMealPlan" :meal-plan="editMealPlan" @updated="planUpdated" />
    <NewMeal v-else @created="requestMeals" class="mb-5" />

    <v-card class="my-2">
      <v-card-title class="headline">
        {{ $t("meal-plan.meal-plans") }}
      </v-card-title>
      <v-divider></v-divider>
    </v-card>
    <v-row dense>
      <v-col :sm="6" :md="6" :lg="4" :xl="3" v-for="(mealplan, i) in plannedMeals" :key="i">
        <v-card class="mt-1">
          <v-card-title class="mb-0 pb-0">
            {{ $d(new Date(mealplan.startDate.replaceAll("-", "/")), "short") }} -
            {{ $d(new Date(mealplan.endDate.replaceAll("-", "/")), "short") }}
          </v-card-title>
          <v-divider class="mx-2 pa-1"></v-divider>
          <v-card-actions class="mb-0 px-2 py-0">
            <v-btn text small v-if="!mealplan.shoppingList" color="info" @click="createShoppingList(mealplan.uid)">
              <v-icon left small>
                mdi-cart-check
              </v-icon>
              {{ $t("shopping-list.create-shopping-list") }}
            </v-btn>
            <v-btn
              text
              small
              v-else
              color="info"
              class="mx-0"
              :to="{ path: '/shopping-list', query: { list: mealplan.shoppingList } }"
            >
              <v-icon left small>
                mdi-cart-check
              </v-icon>
              {{ $t("shopping-list.shopping-list") }}
            </v-btn>
            <v-spacer></v-spacer>
            <TheCopyButton color="info" :copy-text="mealPlanURL(mealplan.uid)">
              {{ $t("general.link-copied") }}
            </TheCopyButton>
          </v-card-actions>

          <v-list class="mt-0 pt-0">
            <v-list-group v-for="(planDay, pdi) in mealplan.planDays" :key="`planDays-${pdi}`">
              <template v-slot:activator>
                <v-list-item-avatar color="primary" class="headline font-weight-light white--text">
                  <v-img :src="getImage(planDay['meals'][0].slug)"></v-img>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title v-html="$d(new Date(planDay.date.replaceAll('-', '/')), 'short')"></v-list-item-title>
                  <v-list-item-subtitle v-html="planDay['meals'][0].name"></v-list-item-subtitle>
                </v-list-item-content>
              </template>

              <v-list-item
                three-line
                v-for="(meal, index) in planDay.meals"
                :key="generateKey(meal.slug, index)"
                :to="meal.slug ? `/recipe/${meal.slug}` : null"
              >
                <v-list-item-avatar color="primary" class="headline font-weight-light white--text">
                  <v-img :src="getImage(meal.slug)"></v-img>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title v-html="meal.name"></v-list-item-title>
                  <v-list-item-subtitle v-html="meal.description"> </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list-group>
          </v-list>

          <v-card-actions class="mt-n3">
            <TheButton small secondary delete @click="deletePlan(mealplan.uid)" />
            <v-spacer></v-spacer>
            <TheButton small edit @click="editPlan(mealplan.uid)" />
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { api } from "@/api";
import { utils } from "@/utils";
import NewMeal from "@/components/MealPlan/MealPlanNew";
import EditPlan from "@/components/MealPlan/MealPlanEditor";
import TheCopyButton from "@/components/UI/Buttons/TheCopyButton";
export default {
  components: {
    NewMeal,
    EditPlan,
    TheCopyButton,
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
    mealPlanURL(uid) {
      return window.location.origin + "/meal-plan?id=" + uid;
    },
    generateKey(name, index) {
      return utils.generateUniqueKey(name, index);
    },
    getImage(image) {
      return api.recipes.recipeTinyImage(image);
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
      if (await api.mealPlans.delete(id)) {
        this.requestMeals();
      }
    },
    async createShoppingList(id) {
      await api.mealPlans.shoppingList(id);
      this.requestMeals();
      this.$store.dispatch("requestCurrentGroup");
    },
    redirectToList(id) {
      this.$router.push(id);
    },
  },
};
</script>

<style></style>
