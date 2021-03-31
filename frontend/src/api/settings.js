import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

const settingsBase = baseURL + "site-settings";

const settingsURLs = {
  siteSettings: `${settingsBase}`,
  updateSiteSettings: `${settingsBase}`,
  testWebhooks: `${settingsBase}/webhooks/test`,
};

export const settingsAPI = {
  async requestAll() {
    let response = await apiReq.get(settingsURLs.siteSettings);
    return response.data;
  },

  async testWebhooks() {
    let response = await apiReq.post(settingsURLs.testWebhooks);
    return response.data;
  },

  async update(body) {
    let response = await apiReq.put(settingsURLs.updateSiteSettings, body);
    return response.data;
  },
};
