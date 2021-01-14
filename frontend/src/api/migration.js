import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import { store } from "../store/store";

const migrationBase = baseURL + "migration/";

const migrationURLs = {
  upload: migrationBase + "upload/",
  delete: (file) => `${migrationBase}${file}/delete/`,
  chowdownURL: migrationBase + "chowdown/repo/",
  nextcloudAvaiable: migrationBase + "nextcloud/available/",
  nextcloudImport: (selection) =>
    `${migrationBase}nextcloud/${selection}/import/`,
};

export default {
  async migrateChowdown(repoURL) {
    let postBody = { url: repoURL };
    let response = await apiReq.post(migrationURLs.chowdownURL, postBody);
    store.dispatch("requestRecentRecipes");
    return response.data;
  },
  async getNextcloudImports() {
    let response = await apiReq.get(migrationURLs.nextcloudAvaiable);
    return response.data;
  },
  async importNextcloud(selected) {
    let response = await apiReq.post(migrationURLs.nextcloudImport(selected));
    return response.data;
  },
  async uploadFile(form_data) {
    let response = await apiReq.post(migrationURLs.upload, form_data, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },
  async delete(file_folder_name) {
    let response = await apiReq.delete(migrationURLs.delete(file_folder_name));
    return response.data;
  },
};
