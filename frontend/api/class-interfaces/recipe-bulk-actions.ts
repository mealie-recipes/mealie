import { BaseAPI } from "../_base";

interface BasePayload {
  recipes: string[];
}

type exportType = "json";

interface RecipeBulkDelete extends BasePayload {}

interface RecipeBulkExport extends BasePayload {
  exportType: exportType;
}

interface RecipeBulkCategorize extends BasePayload {
  categories: string[];
}

interface RecipeBulkTag extends BasePayload {
  tags: string[];
}

interface BulkActionError {
  recipe: string;
  error: string;
}

interface BulkActionResponse {
  success: boolean;
  message: string;
  errors: BulkActionError[];
}

export interface GroupDataExport {
  id: string;
  groupId: string;
  name: string;
  filename: string;
  path: string;
  size: string;
  expires: Date;
}

const prefix = "/api";

const routes = {
  bulkExport: prefix + "/recipes/bulk-actions/export",
  bulkCategorize: prefix + "/recipes/bulk-actions/categorize",
  bulkTag: prefix + "/recipes/bulk-actions/tag",
  bulkDelete: prefix + "/recipes/bulk-actions/delete",
};

export class BulkActionsAPI extends BaseAPI {
  async bulkExport(payload: RecipeBulkExport) {
    return await this.requests.post<BulkActionResponse>(routes.bulkExport, payload);
  }

  async bulkCategorize(payload: RecipeBulkCategorize) {
    return await this.requests.post<BulkActionResponse>(routes.bulkCategorize, payload);
  }

  async bulkTag(payload: RecipeBulkTag) {
    return await this.requests.post<BulkActionResponse>(routes.bulkTag, payload);
  }

  async bulkDelete(payload: RecipeBulkDelete) {
    return await this.requests.post<BulkActionResponse>(routes.bulkDelete, payload);
  }

  async fetchExports() {
    return await this.requests.get<GroupDataExport[]>(routes.bulkExport);
  }
}
