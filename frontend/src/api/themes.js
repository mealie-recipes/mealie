import { apiReq } from "./api-utils";
import i18n from "@/i18n.js";
import { API_ROUTES } from "./apiRoutes";

export const themeAPI = {
  async requestAll() {
    let response = await apiReq.get(API_ROUTES.themes);
    return response.data;
  },

  async requestByName(name) {
    let response = await apiReq.get(API_ROUTES.themesId(name));
    return response.data;
  },

  async create(postBody) {
    return await apiReq.post(
      API_ROUTES.themesCreate,
      postBody,
      () => i18n.t("settings.theme.error-creating-theme-see-log-file"),
      () => i18n.t("settings.theme.theme-saved")
    );
  },

  update(data) {
    return apiReq.put(
      API_ROUTES.themesId(data.id),
      data,
      () => i18n.t("settings.theme.error-updating-theme"),
      () => i18n.t("settings.theme.theme-updated")
    );
  },

  delete(id) {
    return apiReq.delete(
      API_ROUTES.themesId(id),
      null,
      () => i18n.t("settings.theme.error-deleting-theme"),
      () => i18n.t("settings.theme.theme-deleted")
    );
  },
};
