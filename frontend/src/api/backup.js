import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import { store } from "@/store";
import i18n from '@/i18n.js';

const backupBase = baseURL + "backups/";

export const backupURLs = {
  // Backup
  available: `${backupBase}available`,
  createBackup: `${backupBase}export/database`,
  importBackup: fileName => `${backupBase}${fileName}/import`,
  deleteBackup: fileName => `${backupBase}${fileName}/delete`,
  downloadBackup: fileName => `${backupBase}${fileName}/download`,
};



export const backupAPI = {
  /**
   * Request all backups available on the server
   * @returns {Array} List of Available Backups
   */
  async requestAvailable() {
    let response = await apiReq.get(backupURLs.available);
    return response.data;
  },
  /**
   * Calls for importing a file on the server
   * @param {string} fileName
   * @param {object} data
   * @returns A report containing status of imported items
   */
  async import(fileName, data) {
    let response = await apiReq.post(backupURLs.importBackup(fileName), data);
    store.dispatch("requestRecentRecipes");
    return response;
  },
  /**
   * Removes a file from the server
   * @param {string} fileName
   */
  async delete(fileName) {
    return apiReq.delete(
      backupURLs.deleteBackup(fileName),
      null,
      function() { return i18n.t('settings.backup.unable-to-delete-backup'); },
      function() { return i18n.t('settings.backup.backup-deleted'); }
    );
  },
  /**
   * Creates a backup on the serve given a set of options
   * @param {object} data
   * @returns
   */
  async create(options) {
    return apiReq.post(
      backupURLs.createBackup, 
      options,
      function() { return i18n.t('settings.backup.error-creating-backup-see-log-file'); },
      function(response) { return i18n.t('settings.backup.backup-created-at-response-export_path', {path: response.data.export_path}); }
    );
  },
  /**
   * Downloads a file from the server. I don't actually think this is used?
   * @param {string} fileName
   * @returns Download URL
   */
  async download(fileName) {
    const url = backupURLs.downloadBackup(fileName);
    apiReq.download(url);
  },
};
