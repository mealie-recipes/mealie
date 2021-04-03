import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

const prefix = baseURL + "debug";

const debugURLs = {
  version: `${prefix}/version`,
  debug: `${prefix}`,
  lastRecipe: `${prefix}/last-recipe-json`,
  demo: `${prefix}/is-demo`,
};

export const metaAPI = {
  async getAppInfo() {
    let response = await apiReq.get(debugURLs.version);
    return response.data;
  },

  async getDebugInfo() {
    const response = await apiReq.get(debugURLs.debug);
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
