import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import { store } from "../store/store";

const backupBase = baseURL + "backups/";

const backupURLs = {
  // Backup
  available: `${backupBase}available/`,
  createBackup: `${backupBase}export/database/`,
  importBackup: (fileName) => `${backupBase}${fileName}/import/`,
  deleteBackup: (fileName) => `${backupBase}${fileName}/delete/`,
};

export default {
  async requestAvailable() {
    let response = await apiReq.get(backupURLs.available);
    return response.data;
  },

  async import(fileName) {
    let response = await apiReq.post(backupURLs.importBackup(fileName));
    store.dispatch("requestRecentRecipes");
    return response;
  },

  async delete(fileName) {
    await apiReq.delete(backupURLs.deleteBackup(fileName));
  },

  async create(tag, template) {
    if (typeof template == String) {
      template = [template];
    }
    console.log(tag, template);
    let response = apiReq.post(backupURLs.createBackup, {
      tag: tag,
      template: template,
    });
    return response;
  },
};
