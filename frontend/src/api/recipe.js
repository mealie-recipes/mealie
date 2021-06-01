import { API_ROUTES } from "./apiRoutes";
import { apiReq } from "./api-utils";
import { baseURL } from "./api-utils";
import { store } from "../store";
import i18n from "@/i18n.js";

const prefix = baseURL + "recipes/";

const recipeURLs = {
  allRecipes: baseURL + "recipes",
  summary: baseURL + "recipes" + "/summary",
  allRecipesByCategory: prefix + "category",
  create: prefix + "create",
  createByURL: prefix + "create-url",
  recipe: slug => prefix + slug,
  update: slug => prefix + slug,
  delete: slug => prefix + slug,
  createAsset: slug => `${prefix}${slug}/assets`,
  recipeImage: slug => `${prefix}${slug}/image`,
  updateImage: slug => `${prefix}${slug}/image`,
  untagged: prefix + "summary/untagged",
  uncategorized: prefix + "summary/uncategorized ",
};

export const recipeAPI = {
  /**
   * Create a Recipe by URL
   * @param {string} recipeURL
   * @returns {string} Recipe Slug
   */
  async createByURL(recipeURL) {
    const response = await apiReq.post(
      recipeURLs.createByURL,
      { url: recipeURL },
      () => i18n.t("recipe.recipe-creation-failed"),
      () => i18n.t("recipe.recipe-created")
    );

    store.dispatch("requestRecentRecipes");
    return response;
  },

  async getAllByCategory(categories) {
    let response = await apiReq.post(recipeURLs.allRecipesByCategory, categories);
    return response.data;
  },

  async create(recipeData) {
    const response = await apiReq.post(
      recipeURLs.create,
      recipeData,
      () => i18n.t("recipe.recipe-creation-failed"),
      () => i18n.t("recipe.recipe-created")
    );
    store.dispatch("requestRecentRecipes");
    return response.data;
  },

  async requestDetails(recipeSlug) {
    let response = await apiReq.get(recipeURLs.recipe(recipeSlug));
    return response.data;
  },

  updateImage(recipeSlug, fileObject, overrideSuccessMsg = false) {
    const formData = new FormData();
    formData.append("image", fileObject);
    formData.append("extension", fileObject.name.split(".").pop());

    let successMessage = null;
    if (!overrideSuccessMsg) {
      successMessage = function() {
        return overrideSuccessMsg ? null : i18n.t("recipe.recipe-image-updated");
      };
    }

    return apiReq.put(
      recipeURLs.updateImage(recipeSlug),
      formData,
      () => i18n.t("general.image-upload-failed"),
      successMessage
    );
  },

  async createAsset(recipeSlug, fileObject, name, icon) {
    const fd = new FormData();
    fd.append("file", fileObject);
    fd.append("extension", fileObject.name.split(".").pop());
    fd.append("name", name);
    fd.append("icon", icon);
    const response = apiReq.post(recipeURLs.createAsset(recipeSlug), fd);
    return response;
  },

  updateImagebyURL(slug, url) {
    return apiReq.post(
      recipeURLs.updateImage(slug),
      { url: url },
      () => i18n.t("general.image-upload-failed"),
      () => i18n.t("recipe.recipe-image-updated")
    );
  },

  async update(data) {
    let response = await apiReq.put(
      recipeURLs.update(data.slug),
      data,
      () => i18n.t("recipe.recipe-update-failed"),
      () => i18n.t("recipe.recipe-updated")
    );
    if (response) {
      store.dispatch("patchRecipe", response.data);
      return response.data.slug; // ! Temporary until I rewrite to refresh page without additional request
    }
  },

  async patch(data) {
    let response = await apiReq.patch(recipeURLs.update(data.slug), data);
    store.dispatch("patchRecipe", response.data);
    return response.data;
  },

  async delete(recipeSlug) {
    const response = await apiReq.delete(
      recipeURLs.delete(recipeSlug),
      null,
      () => i18n.t("recipe.unable-to-delete-recipe"),
      () => i18n.t("recipe.recipe-deleted")
    );
    store.dispatch("dropRecipe", response.data);
    return response;
  },

  async allSummary(start = 0, limit = 9999) {
    const response = await apiReq.get(recipeURLs.summary, {
      params: { start: start, limit: limit },
    });
    return response.data;
  },

  async allUntagged() {
    const response = await apiReq.get(recipeURLs.untagged);
    return response.data;
  },

  async allUnategorized() {
    const response = await apiReq.get(recipeURLs.uncategorized);
    return response.data;
  },

  recipeImage(recipeSlug, version = null, key = null) {
    return `/api/media/recipes/${recipeSlug}/images/original.webp?&rnd=${key}&version=${version}`;
  },

  recipeSmallImage(recipeSlug, version = null, key = null) {
    return `/api/media/recipes/${recipeSlug}/images/min-original.webp?&rnd=${key}&version=${version}`;
  },

  recipeTinyImage(recipeSlug, version = null, key = null) {
    return `/api/media/recipes/${recipeSlug}/images/tiny-original.webp?&rnd=${key}&version=${version}`;
  },

  recipeAssetPath(recipeSlug, assetName) {
    return `/api/media/recipes/${recipeSlug}/assets/${assetName}`;
  },

  /** Create comment in the Database
   * @param slug
   */
  async createComment(slug, data) {
    const response = await apiReq.post(API_ROUTES.recipesSlugComments(slug), data);
    return response.data;
  },
  /** Update comment in the Database
   * @param slug
   * @param id
   */
  async updateComment(slug, id, data) {
    const response = await apiReq.put(API_ROUTES.recipesSlugCommentsId(slug, id), data);
    return response.data;
  },
  /** Delete comment from the Database
   * @param slug
   * @param id
   */
  async deleteComment(slug, id) {
    const response = await apiReq.delete(API_ROUTES.recipesSlugCommentsId(slug, id));
    return response.data;
  },
};
