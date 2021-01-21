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
  downloadBackup: (fileName) => `${backupBase}${fileName}/download/`,
};

export default {
  async requestAvailable() {
    let response = await apiReq.get(backupURLs.available);
    return response.data;
  },

  async import(fileName, data) {
    let response = await apiReq.post(backupURLs.importBackup(fileName), data);
    store.dispatch("requestRecentRecipes");
    return response;
  },

  async delete(fileName) {
    await apiReq.delete(backupURLs.deleteBackup(fileName));
  },

  async create(data) {
    let response = apiReq.post(backupURLs.createBackup, data);
    return response;
  },
  async download(fileName) {
    let response = await apiReq.get(backupURLs.downloadBackup(fileName));
    return response.data;
  },
};
