import { apiReq } from "./api-utils";
import i18n from "@/i18n.js";
import { API_ROUTES } from "./apiRoutes";

export const aboutAPI = {
  async getEvents() {
    const resposne = await apiReq.get(API_ROUTES.aboutEvents);
    return resposne.data;
  },
  async deleteEvent(id) {
    const resposne = await apiReq.delete(API_ROUTES.aboutEventsId(id));
    return resposne.data;
  },
  async deleteAllEvents() {
    const resposne = await apiReq.delete(API_ROUTES.aboutEvents);
    return resposne.data;
  },

  async allEventNotifications() {
    const response = await apiReq.get(API_ROUTES.aboutEventsNotifications);
    return response.data;
  },

  async createNotification(data) {
    const response = await apiReq.post(API_ROUTES.aboutEventsNotifications, data);
    return response.data;
  },

  async deleteNotification(id) {
    const response = await apiReq.delete(API_ROUTES.aboutEventsNotificationsId(id));
    return response.data;
  },
  async testNotificationByID(id) {
    const response = await apiReq.post(
      API_ROUTES.aboutEventsNotificationsTest,
      { id: id },
      () => i18n.t("events.something-went-wrong"),
      () => i18n.t("events.test-message-sent")
    );
    return response.data;
  },
  async testNotificationByURL(url) {
    const response = await apiReq.post(
      API_ROUTES.aboutEventsNotificationsTest,
      { test_url: url },
      () => i18n.t("events.something-went-wrong"),
      () => i18n.t("events.test-message-sent")
    );
    return response.data;
  },
  //   async getAppInfo() {
  //     const response = await apiReq.get(aboutURLs.version);
  //     return response.data;
  //   },

  //   async getDebugInfo() {
  //     const response = await apiReq.get(aboutURLs.debug);
  //     return response.data;
  //   },

  //   async getLogText(num) {
  //     const response = await apiReq.get(aboutURLs.log(num));
  //     return response.data;
  //   },

  //   async getLastJson() {
  //     const response = await apiReq.get(aboutURLs.lastRecipe);
  //     return response.data;
  //   },

  //   async getIsDemo() {
  //     const response = await apiReq.get(aboutURLs.demo);
  //     return response.data;
  //   },

  //   async getStatistics() {
  //     const response = await apiReq.get(aboutURLs.statistics);
  //     return response.data;
  //   },
};
