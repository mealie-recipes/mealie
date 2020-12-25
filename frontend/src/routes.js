import Home from "./components/Home";
import Page404 from "./components/Page404";
import Recipe from "./components/Recipe";
import NewRecipe from "./components/NewRecipe";
import Admin from "./components/Admin/Admin";
import MealPlanner from "./components/MealPlan/MealPlanner";
import ThisWeek from "./components/MealPlan/ThisWeek";
import api from "./api";

export const routes = [
  { path: "/", component: Home },
  { path: "/mealie", component: Home },
  { path: "/recipe/:recipe", component: Recipe },
  { path: "/new/", component: NewRecipe },
  { path: "/settings/site", component: Admin },
  { path: "/meal-plan/planner", component: MealPlanner },
  { path: "/meal-plan/this-week", component: ThisWeek },
  {
    path: "/meal-plan/today",
    beforeEnter:  async (_to, _from, next) => {
      await todaysMealRoute().then((redirect) => {
        next(redirect);
      });
    },
  },
  { path: "*", component: Page404 },
];

async function todaysMealRoute() {
  const response = await api.mealPlans.today();
  return "/recipe/" + response.data;
}
