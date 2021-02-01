import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

const mealplanBase = baseURL + "meal-plan/";

const mealPlanURLs = {
  // Meals
  create: `${mealplanBase}create/`,
  today: `${mealplanBase}today/`,
  thisWeek: `${mealplanBase}this-week/`,
  all: `${mealplanBase}all/`,
  delete: (planID) => `${mealplanBase}${planID}/delete/`,
  update: (planID) => `${mealplanBase}${planID}/update/`,
};

export default {
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
    let response = await apiReq.post(mealPlanURLs.update(id), body);
    return response;
  },
};
