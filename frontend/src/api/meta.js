import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

const prefix = baseURL + "debug";

const debugURLs = {
  version: `${prefix}/version`,
  debug: `${prefix}`,
  lastRecipe: `${prefix}/last-recipe-json`,
  demo: `${prefix}/is-demo`,
  log: num => `${prefix}/log/${num}`,
  statistics: `${prefix}/statistics`,
};

export const metaAPI = {
  async getAppInfo() {
    const response = await apiReq.get(debugURLs.version);
    return response.data;
  },

  async getDebugInfo() {
    const response = await apiReq.get(debugURLs.debug);
    return response.data;
  },

  async getLogText(num) {
    const response = await apiReq.get(debugURLs.log(num));
    return response.data;
  },

  async getLastJson() {
    const response = await apiReq.get(debugURLs.lastRecipe);
    return response.data;
  },

  async getIsDemo() {
    const response = await apiReq.get(debugURLs.demo);
    return response.data;
  },

  async getStatistics() {
    const response = await apiReq.get(debugURLs.statistics);
    return response.data;
  },
};
