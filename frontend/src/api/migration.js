import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import { store } from "../store/store";

const migrationBase = baseURL + "migration/";

const migrationURLs = {
  chowdownURL: migrationBase + "chowdown/repo/",
  nextcloudAvaiable: migrationBase + "nextcloud/available/",
  nextcloudImport: (selection) =>
    `${migrationBase}nextcloud/${selection}/import/`,
  nextcloudDelete: (selection) =>
    `${migrationBase}nextcloud/${selection}/delete/`,
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
};
