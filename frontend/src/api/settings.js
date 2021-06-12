import { apiReq } from "./api-utils";
import { API_ROUTES } from "./apiRoutes";

export const settingsAPI = {
  async requestAll() {
    let response = await apiReq.get(API_ROUTES.siteSettings);
    return response.data;
  },

  async testWebhooks() {
    let response = await apiReq.post(API_ROUTES.siteSettingsWebhooksTest);
    return response.data;
  },

  async update(body) {
    let response = await apiReq.put(API_ROUTES.siteSettings, body);
    return response.data;
  },
};
