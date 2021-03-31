import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import { store } from "../store";

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
    let response = await apiReq.delete(migrationURLs.delete(folder, file));
    return response.data;
  },
  async import(folder, file) {
    let response = await apiReq.post(migrationURLs.import(folder, file));
    store.dispatch("requestRecentRecipes");
    return response.data;
  },
};
