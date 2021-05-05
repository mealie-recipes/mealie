import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import i18n from "@/i18n.js";

const prefix = baseURL + "themes";

const settingsURLs = {
  allThemes: `${baseURL}themes`,
  specificTheme: id => `${prefix}/${id}`,
  createTheme: `${prefix}/create`,
  updateTheme: id => `${prefix}/${id}`,
  deleteTheme: id => `${prefix}/${id}`,
};

export const themeAPI = {
  async requestAll() {
    let response = await apiReq.get(settingsURLs.allThemes);
    return response.data;
  },

  async requestByName(name) {
    let response = await apiReq.get(settingsURLs.specificTheme(name));
    return response.data;
  },

  async create(postBody) {
    return await apiReq.post(
      settingsURLs.createTheme,
      postBody,
      () => i18n.t("settings.theme.error-creating-theme-see-log-file"),
      () => i18n.t("settings.theme.theme-saved")
    );
  },

  update(data) {
    return apiReq.put(
      settingsURLs.updateTheme(data.id),
      data,
      () => i18n.t("settings.theme.error-updating-theme"),
      () => i18n.t("settings.theme.theme-updated")
    );
  },

  delete(id) {
    return apiReq.delete(
      settingsURLs.deleteTheme(id),
      null,
      () => i18n.t("settings.theme.error-deleting-theme"),
      () => i18n.t("settings.theme.theme-deleted")
    );
  },
};
