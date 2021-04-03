import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import { store } from "../store";
import { router } from "../main";
import qs from "qs";

const prefix = baseURL + "recipes/";

const recipeURLs = {
  allRecipes: baseURL + "recipes",
  allRecipesByCategory: prefix + "category",
  create: prefix + "create",
  createByURL: prefix + "create-url",
  recipe: slug => prefix + slug,
  update: slug => prefix + slug,
  delete: slug => prefix + slug,
  recipeImage: slug => `${prefix}${slug}/image`,
  updateImage: slug => `${prefix}${slug}/image`,
};

export const recipeAPI = {
  /**
   * Create a Recipe by URL
   * @param {string} recipeURL
   * @returns {string} Recipe Slug
   */
  async createByURL(recipeURL) {
    let response = await apiReq.post(recipeURLs.createByURL, {
      url: recipeURL,
    });

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
    let response = await apiReq.post(recipeURLs.create, recipeData);
    store.dispatch("requestRecentRecipes");
    return response.data;
  },

  async requestDetails(recipeSlug) {
    let response = await apiReq.get(recipeURLs.recipe(recipeSlug));
    return response.data;
  },

  async updateImage(recipeSlug, fileObject) {
    const fd = new FormData();
    fd.append("image", fileObject);
    fd.append("extension", fileObject.name.split(".").pop());
    let response = apiReq.put(recipeURLs.updateImage(recipeSlug), fd);
    return response;
  },

  async update(data) {
    let response = await apiReq.put(recipeURLs.update(data.slug), data);
    store.dispatch("requestRecentRecipes");
    return response.data;
  },

  async delete(recipeSlug) {
    await apiReq.delete(recipeURLs.delete(recipeSlug));
    store.dispatch("requestRecentRecipes");
    router.push(`/`);
  },

  async allByKeys(recipeKeys, num = 9999) {
    const response = await apiReq.get(recipeURLs.allRecipes, {
      params: {
        keys: recipeKeys,
        num: num,
      },
      paramsSerializer: params => {
        return qs.stringify(params, { arrayFormat: "repeat" });
      },
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
