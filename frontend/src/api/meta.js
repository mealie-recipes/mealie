import { apiReq } from "./api-utils";
import { API_ROUTES } from "./apiRoutes";

export const metaAPI = {
  async getAppInfo() {
    const response = await apiReq.get(API_ROUTES.debugVersion);
    return response.data;
  },

  async getDebugInfo() {
    const response = await apiReq.get(API_ROUTES.debug);
    return response.data;
  },

  async getLogText(num) {
    const response = await apiReq.get(API_ROUTES.debugLog(num));
    return response.data;
  },

  async getLastJson() {
    const response = await apiReq.get(API_ROUTES.debugLastRecipeJson);
    return response.data;
  },

  async getStatistics() {
    const response = await apiReq.get(API_ROUTES.debugStatistics);
    return response.data;
  },
};
