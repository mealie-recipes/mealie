import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

const prefix = baseURL + "categories";

const categoryURLs = {
  get_all: `${prefix}`,
  get_category: category => `${prefix}/${category}`,
  delete_category: category => `${prefix}/${category}`,
};

export default {
  async getAll() {
    let response = await apiReq.get(categoryURLs.get_all);
    return response.data;
  },
  async get_recipes_in_category(category) {
    let response = await apiReq.get(categoryURLs.get_category(category));
    return response.data;
  },
  async delete(category) {
    let response = await apiReq.delete(categoryURLs.delete_category(category));
    return response.data;
  },
};
