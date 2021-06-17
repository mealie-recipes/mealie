import { apiReq } from "./api-utils";
import { store } from "@/store";
import i18n from "@/i18n.js";
import { API_ROUTES } from "./apiRoutes";

export const siteSettingsAPI = {
  async get() {
    let response = await apiReq.get(API_ROUTES.siteSettings);
    return response.data;
  },

  async update(body) {
    const response = await apiReq.put(
      API_ROUTES.siteSettings,
      body,
      () => i18n.t("settings.settings-update-failed"),
      () => i18n.t("settings.settings-updated")
    );
    if (response) {
      store.dispatch("requestSiteSettings");
    }
    return response;
  },

  async getPages() {
    let response = await apiReq.get(API_ROUTES.siteSettingsCustomPages);
    return response.data;
  },

  async getPage(id) {
    let response = await apiReq.get(API_ROUTES.siteSettingsCustomPagesId(id));
    return response.data;
  },

  createPage(body) {
    return apiReq.post(
      API_ROUTES.siteSettingsCustomPages,
      body,
      () => i18n.t("page.page-creation-failed"),
      () => i18n.t("page.new-page-created")
    );
  },

  async deletePage(id) {
    return await apiReq.delete(
      API_ROUTES.siteSettingsCustomPagesId(id),
      null,
      () => i18n.t("page.page-deletion-failed"),
      () => i18n.t("page.page-deleted")
    );
  },

  updatePage(body) {
    return apiReq.put(
      API_ROUTES.siteSettingsCustomPagesId(body.id),
      body,
      () => i18n.t("page.page-update-failed"),
      () => i18n.t("page.page-updated")
    );
  },

  async updateAllPages(allPages) {
    let response = await apiReq.put(
      API_ROUTES.siteSettingsCustomPages,
      allPages,
      () => i18n.t("page.pages-update-failed"),
      () => i18n.t("page.pages-updated")
    );
    return response;
  },
};
