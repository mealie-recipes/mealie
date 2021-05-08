import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

const prefix = baseURL + "about";

const aboutURLs = {
  version: `${prefix}/version`,
  debug: `${prefix}`,
  lastRecipe: `${prefix}/last-recipe-json`,
  demo: `${prefix}/is-demo`,
  log: num => `${prefix}/log/${num}`,
  statistics: `${prefix}/statistics`,
  events: `${prefix}/events`,
  event: id => `${prefix}/events/${id}`,

  allNotifications: `${prefix}/events/notifications`,
  notification: id => `${prefix}/events/notifications/${id}`,
};

export const aboutAPI = {
  async getEvents() {
    const resposne = await apiReq.get(aboutURLs.events);
    return resposne.data;
  },
  async deleteEvent(id) {
    const resposne = await apiReq.delete(aboutURLs.event(id));
    return resposne.data;
  },
  async deleteAllEvents() {
    const resposne = await apiReq.delete(aboutURLs.events);
    return resposne.data;
  },

  async allEventNotifications() {
    const response = await apiReq.get(aboutURLs.allNotifications);
    return response.data;
  },

  async createNotification(data) {
    const response = await apiReq.post(aboutURLs.allNotifications, data);
    return response.data;
  },

  async deleteNotification(id) {
    const response = await apiReq.delete(aboutURLs.notification(id));
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
