import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import { store } from "../store";
import i18n from '@/i18n.js';

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
  recipeImage: slug => `${prefix}${slug}/image`,
  updateImage: slug => `${prefix}${slug}/image`,
  createAsset: slug => `${prefix}${slug}/asset`,
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
      function() { return i18n.t('recipe.recipe-creation-failed'); },
      function() { return i18n.t('recipe.recipe-created'); }
    );

    store.dispatch("requestRecentRecipes");
    return response;
  },

  async getAllByCategory(categories) {
    let response = await apiReq.post(
      recipeURLs.allRecipesByCategory,
      categories
    );
    return response.data;
  },

  async create(recipeData) {
    const response = await apiReq.post(
      recipeURLs.create, 
      recipeData,
      function() { return i18n.t('recipe.recipe-creation-failed'); },
      function() { return i18n.t('recipe.recipe-created'); }
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
    if(!overrideSuccessMsg) {
      successMessage = function() { return overrideSuccessMsg ? null : i18n.t('recipe.recipe-image-updated'); };
    }
    
    return apiReq.put(
      recipeURLs.updateImage(recipeSlug), 
      formData,
      function() { return i18n.t('general.image-upload-failed'); },
      successMessage
    );
  },

  async updateImagebyURL(slug, url) {
    const response = apiReq.post(recipeURLs.updateImage(slug), { url: url });
    return response;
  },

  async update(data) {
    console.log(data)
    let response = await apiReq.put(recipeURLs.update(data.slug), data);
    store.dispatch("patchRecipe", response.data);
    return response.data.slug; // ! Temporary until I rewrite to refresh page without additional request
  },

  async patch(data) {
    let response = await apiReq.patch(recipeURLs.update(data.slug), data);
    store.dispatch("patchRecipe", response.data);
    return response.data;
  },

  delete(recipeSlug) {
    return apiReq.delete(
      recipeURLs.delete(recipeSlug),
      null,
      function() { return i18n.t('recipe.unable-to-delete-recipe'); },
      function() { return i18n.t('recipe.recipe-deleted'); }
    );
  },

  async allSummary(start = 0, limit = 9999) {
    const response = await apiReq.get(recipeURLs.summary, {
      params: { start: start, limit: limit },
    });
    return response.data;
  },

  recipeImage(recipeSlug) {
    return `/api/recipes/${recipeSlug}/image?image_type=original`;
  },

  recipeSmallImage(recipeSlug) {
    return `/api/recipes/${recipeSlug}/image?image_type=small`;
  },

  recipeTinyImage(recipeSlug) {
    return `/api/recipes/${recipeSlug}/image?image_type=tiny`;
  },
};
