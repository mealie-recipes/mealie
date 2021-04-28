import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import { store } from "@/store";

const prefix = baseURL + "categories";

const categoryURLs = {
  getAll: `${prefix}`,
  getEmpty: `${prefix}/empty`,
  getCategory: category => `${prefix}/${category}`,
  deleteCategory: category => `${prefix}/${category}`,
  updateCategory: category => `${prefix}/${category}`,
};

export const categoryAPI = {
  async getAll() {
    let response = await apiReq.get(categoryURLs.getAll);
    return response.data;
  },
  async getEmpty() {
    let response = await apiReq.get(categoryURLs.getEmpty);
    return response.data;
  },
  async create(name) {
    let response = await apiReq.post(categoryURLs.getAll, { name: name });
    store.dispatch("requestCategories");
    return response.data;
  },
  async getRecipesInCategory(category) {
    let response = await apiReq.get(categoryURLs.getCategory(category));
    return response.data;
  },
  async update(name, newName, overrideRequest = false) {
    let response = await apiReq.put(categoryURLs.updateCategory(name), {
      name: newName,
    });
    if (!overrideRequest) {
      store.dispatch("requestCategories");
    }
    return response.data;
  },
  async delete(category, overrideRequest = false) {
    let response = await apiReq.delete(categoryURLs.deleteCategory(category));
    if (!overrideRequest) {
      store.dispatch("requestCategories");
    }
    return response;
  },
};

const tagPrefix = baseURL + "tags";

const tagURLs = {
  getAll: `${tagPrefix}`,
  getEmpty: `${tagPrefix}/empty`,
  getTag: tag => `${tagPrefix}/${tag}`,
  deleteTag: tag => `${tagPrefix}/${tag}`,
  updateTag: tag => `${tagPrefix}/${tag}`,
};

export const tagAPI = {
  async getAll() {
    let response = await apiReq.get(tagURLs.getAll);
    return response.data;
  },
  async getEmpty() {
    let response = await apiReq.get(tagURLs.getEmpty);
    return response.data;
  },
  async create(name) {
    let response = await apiReq.post(tagURLs.getAll, { name: name });
    store.dispatch("requestTags");
    return response.data;
  },
  async getRecipesInTag(tag) {
    let response = await apiReq.get(tagURLs.getTag(tag));
    return response.data;
  },
  async update(name, newName, overrideRequest = false) {
    let response = await apiReq.put(tagURLs.updateTag(name), { name: newName });

    if (!overrideRequest) {
      store.dispatch("requestTags");
    }

    return response.data;
  },
  async delete(tag, overrideRequest = false) {
    let response = await apiReq.delete(tagURLs.deleteTag(tag));
    if (!overrideRequest) {
      store.dispatch("requestTags");
    }
    return response.data;
  },
};
