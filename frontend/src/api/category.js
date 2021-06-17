import { apiReq } from "./api-utils";
import { store } from "@/store";
import i18n from "@/i18n.js";
import { API_ROUTES } from "./apiRoutes";

export const categoryAPI = {
  async getAll() {
    let response = await apiReq.get(API_ROUTES.categories);
    return response.data;
  },
  async getEmpty() {
    let response = await apiReq.get(API_ROUTES.categoriesEmpty);
    return response.data;
  },
  async create(name) {
    const response = await apiReq.post(
      API_ROUTES.categories,
      { name: name },
      () => i18n.t("category.category-creation-failed"),
      () => i18n.t("category.category-created")
    );
    if (response) {
      store.dispatch("requestCategories");
      return response.data;
    }
  },
  async getRecipesInCategory(category) {
    let response = await apiReq.get(API_ROUTES.categoriesCategory(category));
    return response.data;
  },
  async update(name, newName, overrideRequest = false) {
    const response = await apiReq.put(
      API_ROUTES.categoriesCategory(name),
      { name: newName },
      () => i18n.t("category.category-update-failed"),
      () => i18n.t("category.category-updated")
    );
    if (response && !overrideRequest) {
      store.dispatch("requestCategories");
      return response.data;
    }
  },
  async delete(category, overrideRequest = false) {
    const response = await apiReq.delete(
      API_ROUTES.categoriesCategory(category),
      null,
      () => i18n.t("category.category-deletion-failed"),
      () => i18n.t("category.category-deleted")
    );
    if (response && !overrideRequest) {
      store.dispatch("requestCategories");
    }
    return response;
  },
};

export const tagAPI = {
  async getAll() {
    let response = await apiReq.get(API_ROUTES.tags);
    return response.data;
  },
  async getEmpty() {
    let response = await apiReq.get(API_ROUTES.tagsEmpty);
    return response.data;
  },
  async create(name) {
    const response = await apiReq.post(
      API_ROUTES.tags,
      { name: name },
      () => i18n.t("tag.tag-creation-failed"),
      () => i18n.t("tag.tag-created")
    );
    if (response) {
      store.dispatch("requestTags");
      return response.data;
    }
  },
  async getRecipesInTag(tag) {
    let response = await apiReq.get(API_ROUTES.tagsTag(tag));
    return response.data;
  },
  async update(name, newName, overrideRequest = false) {
    const response = await apiReq.put(
      API_ROUTES.tagsTag(name),
      { name: newName },
      () => i18n.t("tag.tag-update-failed"),
      () => i18n.t("tag.tag-updated")
    );

    if (response) {
      if (!overrideRequest) {
        store.dispatch("requestTags");
      }
      return response.data;
    }
  },
  async delete(tag, overrideRequest = false) {
    const response = await apiReq.delete(
      API_ROUTES.tagsTag(tag),
      null,
      () => i18n.t("tag.tag-deletion-failed"),
      () => i18n.t("tag.tag-deleted")
    );
    if (response) {
      if (!overrideRequest) {
        store.dispatch("requestTags");
      }
      return response.data;
    }
  },
};
