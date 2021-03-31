import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

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
  async create(postBody) {
    let response = await apiReq.post(mealPlanURLs.create, postBody);
    return response;
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

  async delete(id) {
    let response = await apiReq.delete(mealPlanURLs.delete(id));
    return response;
  },

  async update(id, body) {
    let response = await apiReq.put(mealPlanURLs.update(id), body);
    return response;
  },

  async shoppingList(id) {
    let response = await apiReq.get(mealPlanURLs.shopping(id));
    return response.data;
  },
};
