import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import i18n from "@/i18n.js";

const prefix = baseURL + "meal-plans/";

const mealPlanURLs = {
  // Meals
  all: `${prefix}all`,
  create: `${prefix}create`,
  thisWeek: `${prefix}this-week`,
  byId: planID => `${prefix}${planID}`,
  update: planID => `${prefix}${planID}`,
  delete: planID => `${prefix}${planID}`,
  today: `${prefix}today`,
  shopping: planID => `${prefix}${planID}/shopping-list`,
};

export const mealplanAPI = {
  create(postBody) {
    return apiReq.post(
      mealPlanURLs.create,
      postBody,
      () => i18n.t("meal-plan.mealplan-creation-failed"),
      () => i18n.t("meal-plan.mealplan-created")
    );
  },

  async all() {
    let response = await apiReq.get(mealPlanURLs.all);
    return response;
  },

  async thisWeek() {
    let response = await apiReq.get(mealPlanURLs.thisWeek);
    return response.data;
  },

  async today() {
    let response = await apiReq.get(mealPlanURLs.today);
    return response;
  },

  async getById(id) {
    let response = await apiReq.get(mealPlanURLs.byId(id));
    return response.data;
  },

  delete(id) {
    return apiReq.delete(
      mealPlanURLs.delete(id),
      null,
      () => i18n.t("meal-plan.mealplan-deletion-failed"),
      () => i18n.t("meal-plan.mealplan-deleted")
    );
  },

  update(id, body) {
    return apiReq.put(
      mealPlanURLs.update(id),
      body,
      () => i18n.t("meal-plan.mealplan-update-failed"),
      () => i18n.t("meal-plan.mealplan-updated")
    );
  },

  async shoppingList(id) {
    let response = await apiReq.get(mealPlanURLs.shopping(id));
    return response.data;
  },
};
