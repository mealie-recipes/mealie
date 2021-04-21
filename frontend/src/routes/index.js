import HomePage from "@/pages/HomePage";
import Page404 from "@/pages/404Page";
import SearchPage from "@/pages/SearchPage";
import ViewRecipe from "@/pages/Recipe/ViewRecipe";
import NewRecipe from "@/pages/Recipe/NewRecipe";
import CustomPage from "@/pages/Recipes/CustomPage";
import AllRecipes from "@/pages/Recipes/AllRecipes";
import CategoryPage from "@/pages/Recipes/CategoryPage";
import TagPage from "@/pages/Recipes/TagPage";
import Planner from "@/pages/MealPlan/Planner";
import Debug from "@/pages/Debug";
import LoginPage from "@/pages/LoginPage";
import SignUpPage from "@/pages/SignUpPage";
import ThisWeek from "@/pages/MealPlan/ThisWeek";
import { api } from "@/api";
import Admin from "./admin";
import { store } from "../store";
import i18n from "@/i18n.js";

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
  { path: "/sign-up", redirect: "/" },
  { path: "/sign-up/:token", component: SignUpPage },
  { path: "/debug", component: Debug },
  {
    path: "/search",
    component: SearchPage,
    meta: {
      title: i18n.t("search.search"),
    },
  },
  { path: "/recipes/all", component: AllRecipes },
  { path: "/pages/:customPage", component: CustomPage },
  { path: "/recipes/tag/:tag", component: TagPage },
  { path: "/recipes/category/:category", component: CategoryPage },
  {
    path: "/recipe/:recipe",
    component: ViewRecipe,
    meta: {
      title: async route => {
        const recipe = await api.recipes.requestDetails(route.params.recipe);
        return recipe.name;
      },
    },
  },
  { path: "/new/", component: NewRecipe },
  {
    path: "/meal-plan/planner",
    component: Planner,
    meta: {
      title: i18n.t("meal-plan.meal-planner"),
    },
  },
  {
    path: "/meal-plan/this-week",
    component: ThisWeek,
    meta: {
      title: i18n.t("meal-plan.dinner-this-week"),
    },
  },
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
