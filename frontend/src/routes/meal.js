import Planner from "@/pages/MealPlan/Planner";
import ThisWeek from "@/pages/MealPlan/ThisWeek";
import { api } from "@/api";

export const mealRoutes = [
  {
    path: "/meal-plan/planner",
    component: Planner,
    meta: {
      title: "meal-plan.meal-planner",
    },
  },
  {
    path: "/meal-plan/this-week",
    component: ThisWeek,
    meta: {
      title: "meal-plan.dinner-this-week",
    },
  },
  {
    path: "/meal-plan/today",
    beforeEnter: async (_to, _from, next) => {
      await todaysMealRoute().then(redirect => {
        next(redirect);
      });
    },
  },
];

async function todaysMealRoute() {
  const response = await api.mealPlans.today();
  return "/recipe/" + response.data;
}
