import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import { store } from "../store";
import i18n from '@/i18n.js';

const migrationBase = baseURL + "migrations";

const migrationURLs = {
  // New
  all: migrationBase,
  delete: (folder, file) => `${migrationBase}/${folder}/${file}/delete`,
  import: (folder, file) => `${migrationBase}/${folder}/${file}/import`,
};

export const migrationAPI = {
  async getMigrations() {
    let response = await apiReq.get(migrationURLs.all);
    return response.data;
  },
  async delete(folder, file) {
    const response = await apiReq.delete(
      migrationURLs.delete(folder, file),
      null,
      function() { return i18n.t('general.file-folder-not-found'); },
      function() { return i18n.t('migration.migration-data-removed'); }
    );
    return response;
  },
  async import(folder, file) {
    let response = await apiReq.post(migrationURLs.import(folder, file));
    store.dispatch("requestRecentRecipes");
    return response.data;
  },
};
