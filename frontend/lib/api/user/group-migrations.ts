import { BaseAPI } from "../base/base-clients";
import { ReportSummary } from "~/types/api-types/reports";
import { SupportedMigrations } from "~/types/api-types/group";

const prefix = "/api";
export interface MigrationPayload {
  addMigrationTag: boolean;
  migrationType: SupportedMigrations;
  archive: File;
}

const routes = {
  base: `${prefix}/groups/migrations`,
};

export class GroupMigrationApi extends BaseAPI {
  async startMigration(payload: MigrationPayload) {
    const form = new FormData();
    form.append("add_migration_tag", String(payload.addMigrationTag));
    form.append("migration_type", payload.migrationType);
    form.append("archive", payload.archive);

    console.log(form);

    return await this.requests.post<ReportSummary>(routes.base, form);
  }
}
