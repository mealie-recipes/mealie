import { apiReq } from "./api-utils";
import { store } from "../store";
import i18n from "@/i18n.js";
import { API_ROUTES } from "./apiRoutes";

export const migrationAPI = {
  async getMigrations() {
    let response = await apiReq.get(API_ROUTES.migrations);
    return response.data;
  },
  async delete(folder, file) {
    const response = await apiReq.delete(
      API_ROUTES.migrationsImportTypeFileNameDelete(folder, file),
      null,
      () => i18n.t("general.file-folder-not-found"),
      () => i18n.t("migration.migration-data-removed")
    );
    return response;
  },
  async import(folder, file) {
    let response = await apiReq.post(API_ROUTES.migrationsImportTypeFileNameImport(folder, file));
    store.dispatch("requestRecentRecipes");
    return response.data;
  },
};
