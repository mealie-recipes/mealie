import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

const categoryBase = baseURL + "/recipes/categories";

const categoryURLs = {
  get_all: `${categoryBase}/all/`,
  get_category: (category) => `${categoryBase}/${category}/`,
};

export default {
  async get_all() {
    let response = await apiReq.get(categoryURLs.get_all);
    return response.data;
  },
  async get_recipes_in_category(category) {
    let response = await apiReq.get(categoryURLs.get_category(category));
    return response.data;
  },
};
