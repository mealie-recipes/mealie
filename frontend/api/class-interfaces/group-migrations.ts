import { BaseAPI } from "../_base";
import { ReportSummary } from "./group-reports";

const prefix = "/api";

export type SupportedMigration = "nextcloud" | "chowdown";

export interface MigrationPayload {
  migrationType: SupportedMigration;
  archive: File;
}

const routes = {
  base: `${prefix}/groups/migrations`,
};

export class GroupMigrationApi extends BaseAPI {
  async startMigration(payload: MigrationPayload) {
    const form = new FormData();
    form.append("migration_type", payload.migrationType);
    form.append("archive", payload.archive);

    console.log(form);

    return await this.requests.post<ReportSummary>(routes.base, form);
  }
}
