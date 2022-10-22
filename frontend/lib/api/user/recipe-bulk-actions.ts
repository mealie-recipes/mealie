import { BaseAPI } from "../base/base-clients";
import { AssignCategories, AssignSettings, AssignTags, DeleteRecipes, ExportRecipes } from "~/lib/api/types/recipe";
import { GroupDataExport } from "~/lib/api/types/group";

// Many bulk actions return nothing
// eslint-disable-next-line @typescript-eslint/no-empty-interface
interface BulkActionResponse {}

const prefix = "/api";

const routes = {
  bulkExport: prefix + "/recipes/bulk-actions/export",
  purgeExports: prefix + "/recipes/bulk-actions/export/purge",
  bulkCategorize: prefix + "/recipes/bulk-actions/categorize",
  bulkTag: prefix + "/recipes/bulk-actions/tag",
  bulkDelete: prefix + "/recipes/bulk-actions/delete",
  bulkSettings: prefix + "/recipes/bulk-actions/settings",
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

  async fetchExports() {
    return await this.requests.get<GroupDataExport[]>(routes.bulkExport);
  }

  async purgeExports() {
    return await this.requests.delete<BulkActionResponse>(routes.purgeExports);
  }
}
