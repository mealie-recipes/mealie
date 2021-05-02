import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import i18n from "@/i18n.js";

const prefix = baseURL + "themes";

const settingsURLs = {
  allThemes: `${baseURL}themes`,
  specificTheme: themeName => `${prefix}/${themeName}`,
  createTheme: `${prefix}/create`,
  updateTheme: themeName => `${prefix}/${themeName}`,
  deleteTheme: themeName => `${prefix}/${themeName}`,
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

  update(themeName, colors) {
    const body = {
      name: themeName,
      colors: colors,
    };
    return apiReq.put(
      settingsURLs.updateTheme(themeName),
      body,
      () => i18n.t("settings.theme.error-updating-theme"),
      () => i18n.t("settings.theme.theme-updated")
    );
  },

  delete(themeName) {
    return apiReq.delete(
      settingsURLs.deleteTheme(themeName),
      null,
      () => i18n.t("settings.theme.error-deleting-theme"),
      () => i18n.t("settings.theme.theme-deleted")
    );
  },
};
