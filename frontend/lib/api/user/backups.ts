import { BaseAPI } from "../base/base-clients";
import { AllBackups, BackupOptions, CreateBackup } from "~/types/api-types/admin";

const prefix = "/api";

const routes = {
  backupsAvailable: `${prefix}/backups/available`,
  backupsExportDatabase: `${prefix}/backups/export/database`,
  backupsUpload: `${prefix}/backups/upload`,

  backupsFileNameDownload: (fileName: string) => `${prefix}/backups/${fileName}/download`,
  backupsFileNameImport: (fileName: string) => `${prefix}/backups/${fileName}/import`,
  backupsFileNameDelete: (fileName: string) => `${prefix}/backups/${fileName}/delete`,
};

export class BackupAPI extends BaseAPI {
  /** Returns a list of available .zip files for import into Mealie.
   */
  async getAll() {
    return await this.requests.get<AllBackups>(routes.backupsAvailable);
  }

  /** Generates a backup of the recipe database in json format.
   */
  async createOne(payload: CreateBackup) {
    return await this.requests.post(routes.backupsExportDatabase, payload);
  }

  /** Import a database backup file generated from Mealie.
   */
  async restoreDatabase(fileName: string, payload: BackupOptions) {
    return await this.requests.post(routes.backupsFileNameImport(fileName), { name: fileName, ...payload });
  }

  /** Removes a database backup from the file system
   */
  async deleteOne(fileName: string) {
    return await this.requests.delete(routes.backupsFileNameDelete(fileName));
  }
}
