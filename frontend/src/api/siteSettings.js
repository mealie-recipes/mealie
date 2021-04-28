import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import { store } from "@/store";
import i18n from '@/i18n.js';

const settingsBase = baseURL + "site-settings";

const settingsURLs = {
  siteSettings: `${settingsBase}`,
  updateSiteSettings: `${settingsBase}`,
  testWebhooks: `${settingsBase}/webhooks/test`,
  customPages: `${settingsBase}/custom-pages`,
  customPage: id => `${settingsBase}/custom-pages/${id}`,
};

export const siteSettingsAPI = {
  async get() {
    let response = await apiReq.get(settingsURLs.siteSettings);
    return response.data;
  },

  async update(body) {
    const response = await apiReq.put(
      settingsURLs.updateSiteSettings, 
      body,
      function() { return i18n.t('settings.settings-update-failed'); },
      function() { return i18n.t('settings.settings-updated'); }
    );
    if(response) {
      store.dispatch("requestSiteSettings");
    }
    return response;
  },

  async getPages() {
    let response = await apiReq.get(settingsURLs.customPages);
    return response.data;
  },

  async getPage(id) {
    let response = await apiReq.get(settingsURLs.customPage(id));
    return response.data;
  },

  createPage(body) {
    return apiReq.post(
      settingsURLs.customPages, 
      body,
      function() { return i18n.t('page.page-creation-failed'); },
      function() { return i18n.t('page.new-page-created'); }
    );
  },

  async deletePage(id) {
    return await apiReq.delete(
      settingsURLs.customPage(id),
      null,
      function() { return i18n.t('page.page-deletion-failed'); },
      function() { return i18n.t('page.page-deleted'); });
  },

  updatePage(body) {
    return apiReq.put(
      settingsURLs.customPage(body.id),
      body,
      function() { return i18n.t('page.page-update-failed'); },
      function() { return i18n.t('page.page-updated'); }
    );
  },

  async updateAllPages(allPages) {
    let response = await apiReq.put(
      settingsURLs.customPages, 
      allPages,
      function() { return i18n.t('page.pages-update-failed'); },
      function() { return i18n.t('page.pages-updated'); }
    );
    return response;
  },
};
