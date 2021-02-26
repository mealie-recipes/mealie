import HomePage from "../pages/HomePage";
import Page404 from "../pages/404Page";
import SearchPage from "../pages/SearchPage";
import RecipePage from "../pages/RecipePage";
import RecipeNewPage from "../pages/RecipeNewPage";
import AllRecipesPage from "../pages/AllRecipesPage";
import CategoryPage from "../pages/CategoryPage";
import MeaplPlanPage from "../pages/MealPlanPage";
import Debug from "../pages/Debug";
import LoginPage from "../pages/LoginPage";
import MealPlanThisWeekPage from "../pages/MealPlanThisWeekPage";
import api from "@/api";
import Admin from "./admin";
import { store } from "../store";

export const routes = [
  { path: "/", name: "home", component: HomePage },
  {
    path: "/logout",
    beforeEnter: (_to, _from, next) => {
      store.commit("setToken", "");
      store.commit("setIsLoggedIn", false);
      next("/");
    },
  },
  { path: "/mealie", component: HomePage },
  { path: "/login", component: LoginPage },
  { path: "/debug", component: Debug },
  { path: "/search", component: SearchPage },
  { path: "/recipes/all", component: AllRecipesPage },
  { path: "/recipes/:category", component: CategoryPage },
  { path: "/recipe/:recipe", component: RecipePage },
  { path: "/new/", component: RecipeNewPage },
  { path: "/meal-plan/planner", component: MeaplPlanPage },
  { path: "/meal-plan/this-week", component: MealPlanThisWeekPage },
  Admin,
  {
    path: "/meal-plan/today",
    beforeEnter: async (_to, _from, next) => {
      await todaysMealRoute().then(redirect => {
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
