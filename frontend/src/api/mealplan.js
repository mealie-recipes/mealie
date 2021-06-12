import { apiReq } from "./api-utils";
import i18n from "@/i18n.js";
import { API_ROUTES } from "./apiRoutes";

export const mealplanAPI = {
  create(postBody) {
    return apiReq.post(
      API_ROUTES.mealPlansCreate,
      postBody,
      () => i18n.t("meal-plan.mealplan-creation-failed"),
      () => i18n.t("meal-plan.mealplan-created")
    );
  },

  async all() {
    let response = await apiReq.get(API_ROUTES.mealPlansAll);
    return response;
  },

  async thisWeek() {
    let response = await apiReq.get(API_ROUTES.mealPlansThisWeek);
    return response.data;
  },

  async today() {
    let response = await apiReq.get(API_ROUTES.mealPlansToday);
    return response;
  },

  async getById(id) {
    let response = await apiReq.get(API_ROUTES.mealPlansId(id));
    return response.data;
  },

  delete(id) {
    return apiReq.delete(
      API_ROUTES.mealPlansId(id),
      null,
      () => i18n.t("meal-plan.mealplan-deletion-failed"),
      () => i18n.t("meal-plan.mealplan-deleted")
    );
  },

  update(id, body) {
    return apiReq.put(
      API_ROUTES.mealPlansId(id),
      body,
      () => i18n.t("meal-plan.mealplan-update-failed"),
      () => i18n.t("meal-plan.mealplan-updated")
    );
  },

  async shoppingList(id) {
    let response = await apiReq.get(API_ROUTES.mealPlansIdShoppingList(id));
    return response.data;
  },
};
