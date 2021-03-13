import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

const settingsBase = baseURL + "site-settings";

const settingsURLs = {
  siteSettings: `${settingsBase}`,
  updateSiteSettings: `${settingsBase}`,
  testWebhooks: `${settingsBase}/webhooks/test`,
};

export default {
  async get() {
    let response = await apiReq.get(settingsURLs.siteSettings);
    return response.data;
  },

  async update(body) {
    let response = await apiReq.put(settingsURLs.updateSiteSettings, body);
    return response.data;
  },
};
