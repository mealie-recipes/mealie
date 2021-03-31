import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import { store } from "@/store";

const prefix = baseURL + "categories";

const categoryURLs = {
  get_all: `${prefix}`,
  get_category: category => `${prefix}/${category}`,
  delete_category: category => `${prefix}/${category}`,
};

export const categoryAPI = {
  async getAll() {
    let response = await apiReq.get(categoryURLs.get_all);
    return response.data;
  },
  async create(name) {
    let response = await apiReq.post(categoryURLs.get_all, { name: name });
    store.dispatch("requestCategories");
    return response.data;
  },
  async getRecipesInCategory(category) {
    let response = await apiReq.get(categoryURLs.get_category(category));
    return response.data;
  },
  async delete(category) {
    let response = await apiReq.delete(categoryURLs.delete_category(category));
    store.dispatch("requestCategories");
    return response.data;
  },
};

const tagPrefix = baseURL + "tags";

const tagURLs = {
  getAll: `${tagPrefix}`,
  getTag: tag => `${tagPrefix}/${tag}`,
  deleteTag: tag => `${tagPrefix}/${tag}`,
};

export const tagAPI = {
  async getAll() {
    let response = await apiReq.get(tagURLs.getAll);
    return response.data;
  },
  async getRecipesInTag(tag) {
    let response = await apiReq.get(tagURLs.getTag(tag));
    return response.data;
  },
  async delete(tag) {
    let response = await apiReq.delete(tagURLs.deleteTag(tag));
    store.dispatch("requestTags");
    return response.data;
  },
};
