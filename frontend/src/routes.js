import HomePage from "./pages/HomePage";
import Page404 from "./pages/404Page";
import SearchPage from "./pages/SearchPage";
import RecipePage from "./pages/RecipePage";
import RecipeNewPage from "./pages/RecipeNewPage";
import SettingsPage from "./pages/SettingsPage";
import MeaplPlanPage from "./pages/MealPlanPage";
import MealPlanThisWeekPage from "./pages/MealPlanThisWeekPage";
import api from "./api";

export const routes = [
  { path: "/", component: HomePage },
  { path: "/mealie", component: HomePage },
  { path: "/search", component: SearchPage },
  { path: "/recipe/:recipe", component: RecipePage },
  { path: "/new/", component: RecipeNewPage },
  { path: "/settings/site", component: SettingsPage },
  { path: "/meal-plan/planner", component: MeaplPlanPage },
  { path: "/meal-plan/this-week", component: MealPlanThisWeekPage },
  {
    path: "/meal-plan/today",
    beforeEnter: async (_to, _from, next) => {
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
