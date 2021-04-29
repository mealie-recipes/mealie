import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import i18n from '@/i18n.js';

const prefix = baseURL + "meal-plans/";

const mealPlanURLs = {
  // Meals
  all: `${prefix}all`,
  create: `${prefix}create`,
  thisWeek: `${prefix}this-week`,
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
      function() { return i18n.t('meal-plan.mealplan-creation-failed')},
      function() { return i18n.t('meal-plan.mealplan-created'); }
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

  delete(id) {
    return apiReq.delete(mealPlanURLs.delete(id),
      null,
      function() { return i18n.t('meal-plan.mealplan-deletion-failed'); },
      function() { return i18n.t('meal-plan.mealplan-deleted'); }
    );
  },

  update(id, body) {
    return apiReq.put(
      mealPlanURLs.update(id), 
      body,
      function() { return i18n.t('meal-plan.mealplan-update-failed'); },
      function() { return i18n.t('meal-plan.mealplan-updated'); }
    );
  },

  async shoppingList(id) {
    let response = await apiReq.get(mealPlanURLs.shopping(id));
    return response.data;
  },
};
