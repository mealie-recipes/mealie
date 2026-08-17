import { BaseAPI } from "../base/base-clients";
import type {
  AssignCategories,
  AssignSettings,
  AssignTags,
  BulkOrganizeRecipes,
  DeleteRecipes,
  ExportRecipes,
  RecipeSummary,
} from "~/lib/api/types/recipe";
import type { GroupDataExport } from "~/lib/api/types/group";

// Many bulk actions return nothing

type BulkActionResponse = object;

const prefix = "/api";

const routes = {
  bulkExport: prefix + "/recipes/bulk-actions/export",
  purgeExports: prefix + "/recipes/bulk-actions/export/purge",
  bulkCategorize: prefix + "/recipes/bulk-actions/categorize",
  bulkTag: prefix + "/recipes/bulk-actions/tag",
  bulkDelete: prefix + "/recipes/bulk-actions/delete",
  bulkSettings: prefix + "/recipes/bulk-actions/settings",
  bulkOrganize: prefix + "/recipes/bulk-actions/organize",
};

export class BulkActionsAPI extends BaseAPI {
  async bulkExport(payload: ExportRecipes) {
    return await this.requests.post<BulkActionResponse>(routes.bulkExport, payload);
  }

  async bulkCategorize(payload: AssignCategories) {
    return await this.requests.post<BulkActionResponse>(routes.bulkCategorize, payload);
  }

  async bulkSetSettings(payload: AssignSettings) {
    return await this.requests.post<BulkActionResponse>(routes.bulkSettings, payload);
  }

  async bulkTag(payload: AssignTags) {
    return await this.requests.post<BulkActionResponse>(routes.bulkTag, payload);
  }

  async bulkDelete(payload: DeleteRecipes) {
    return await this.requests.post<BulkActionResponse>(routes.bulkDelete, payload);
  }

  async bulkOrganize(payload: BulkOrganizeRecipes) {
    return await this.requests.post<RecipeSummary[]>(routes.bulkOrganize, payload);
  }

  async fetchExports() {
    return await this.requests.get<GroupDataExport[]>(routes.bulkExport);
  }

  async purgeExports() {
    return await this.requests.delete<BulkActionResponse>(routes.purgeExports);
  }
}
