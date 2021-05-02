import Planner from "@/pages/MealPlan/Planner";
import ThisWeek from "@/pages/MealPlan/ThisWeek";
import { api } from "@/api";

import i18n from "@/i18n.js";
import utils from "@/utils";

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
        if (redirect) {
          next(redirect);
        } else {
          utils.notify.error(i18n.t("meal-plan.no-meal-planned-for-today"));
          next(_from);
        }
      });
    },
  },
];

async function todaysMealRoute() {
  const response = await api.mealPlans.today();
  if (response.status == 200 && response.data) {
    return "/recipe/" + response.data;
  } else {
    return null;
  }
}
