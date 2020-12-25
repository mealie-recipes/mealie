import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import { store } from "../store/store";
import { router } from "../main";
import qs from "qs";

const recipeBase = baseURL + "recipe/";

const recipeURLs = {
  // Recipes
  allRecipes: baseURL + "all-recipes/",
  recipe: (slug) => recipeBase + slug + "/",
  recipeImage: (slug) => recipeBase + "image/" + slug + "/",
  createByURL: recipeBase + "create-url/",
  create: recipeBase + "create/",
  updateImage: (slug) => `${recipeBase}${slug}/update/image/`,
  update: (slug) => `${recipeBase}${slug}/update/`,
  delete: (slug) => `${recipeBase}${slug}/delete/`,
};

export default {
  async createByURL(recipeURL) {
    let response = await apiReq.post(recipeURLs.createByURL, { url: recipeURL });
    let recipeSlug = response.data;
    store.dispatch("requestRecentRecipes");
    router.push(`/recipe/${recipeSlug}`);
  },

  async create(recipeData) {
    let response = await apiReq.post(recipeURLs.create, recipeData);
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

    let response = apiReq.post(recipeURLs.updateImage(recipeSlug), fd);

    return response;
  },

  async update(data) {
    const recipeSlug = data.slug;

    apiReq.post(recipeURLs.update(recipeSlug), data);
    store.dispatch("requestRecentRecipes");
  },

  async delete(recipeSlug) {
    apiReq.delete(recipeURLs.delete(recipeSlug));
    store.dispatch("requestRecentRecipes");
    router.push(`/`);
  },

  async allByKeys(recipeKeys, num = 100) {
    const response = await apiReq.get(recipeURLs.allRecipes, {
      params: {
        keys: recipeKeys,
        num: num,
      },
      paramsSerializer: (params) => {
        return qs.stringify(params, { arrayFormat: "repeat" });
      },
    });

    return response.data;
  },
};
