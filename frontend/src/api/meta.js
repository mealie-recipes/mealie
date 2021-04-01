import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

const prefix = baseURL + "debug";

const debugURLs = {
  version: `${prefix}/version`,
  lastRecipe: `${prefix}/last-recipe-json`,
  demo: `${prefix}/is-demo`,
};

export const metaAPI = {
  async get_version() {
    let response = await apiReq.get(debugURLs.version);
    return response.data;
  },
  async getLastJson() {
    let response = await apiReq.get(debugURLs.lastRecipe);
    return response.data;
  },

  async getIsDemo() {
    let response = await apiReq.get(debugURLs.demo);
    return response.data;
  },
};
