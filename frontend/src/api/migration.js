import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import { store } from "../store/store";

const migrationBase = baseURL + "migration/";

const migrationURLs = {
  chowdownURL: migrationBase + "chowdown/repo/",
};

export default {
  async migrateChowdown(repoURL) {
    let postBody = { url: repoURL };
    let response = await apiReq.post(migrationURLs.chowdownURL, postBody);
    console.log(response);
    store.dispatch("requestRecentRecipes");
    return response.data;
  },
};
