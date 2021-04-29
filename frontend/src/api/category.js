import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import { store } from "@/store";
import i18n from '@/i18n.js';

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
    const response = await apiReq.post(
      categoryURLs.getAll, 
      { name: name },
      function() { return i18n.t('category.category-creation-failed'); },
      function() { return i18n.t('category.category-created'); }
    );
    if(response) {
      store.dispatch("requestCategories");
      return response.data;
    }
  },
  async getRecipesInCategory(category) {
    let response = await apiReq.get(categoryURLs.getCategory(category));
    return response.data;
  },
  async update(name, newName, overrideRequest = false) {
    const response = await apiReq.put(
      categoryURLs.updateCategory(name), 
      { name: newName },
      function() { return i18n.t('category.category-update-failed'); },
      function() { return i18n.t('category.category-updated'); }
    );
    if (response && !overrideRequest) {
      store.dispatch("requestCategories");
      return response.data;
    }
  },
  async delete(category, overrideRequest = false) {
    const response = await apiReq.delete(
      categoryURLs.deleteCategory(category),
      null,
      function() { return i18n.t('category.category-deletion-failed'); },
      function() { return i18n.t('category.category-deleted'); }
    );
    if (response && !overrideRequest) {
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
    const response = await apiReq.post(
      tagURLs.getAll, 
      { name: name },
      function() { return i18n.t('tag.tag-creation-failed'); },
      function() { return i18n.t('tag.tag-created'); }
    );
    if(response) {
      store.dispatch("requestTags");
      return response.data;
    }
  },
  async getRecipesInTag(tag) {
    let response = await apiReq.get(tagURLs.getTag(tag));
    return response.data;
  },
  async update(name, newName, overrideRequest = false) {
    const response = await apiReq.put(
      tagURLs.updateTag(name), 
      { name: newName },
      function() { return i18n.t('tag.tag-update-failed'); },
      function() { return i18n.t('tag.tag-updated'); }
    );

    if(response) {
      if (!overrideRequest) {
        store.dispatch("requestTags");
      }
      return response.data;
    }
  },
  async delete(tag, overrideRequest = false) {
    const response = await apiReq.delete(
      tagURLs.deleteTag(tag),
      null,
      function() { return i18n.t('tag.tag-deletion-failed'); },
      function() { return i18n.t('tag.tag-deleted'); }
    );
    if(response) {
      if (!overrideRequest) {
        store.dispatch("requestTags");
      }
      return response.data;
    }
  },
};
