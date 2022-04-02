import { BaseAPI } from "../_base";
import { AdminAboutInfo, DockerVolumeText, CheckAppConfig } from "~/types/api-types/admin";

const prefix = "/api";

const routes = {
  about: `${prefix}/admin/about`,
  aboutStatistics: `${prefix}/admin/about/statistics`,
  check: `${prefix}/admin/about/check`,
  docker: `${prefix}/admin/about/docker/validate`,
  validationFile: `${prefix}/media/docker/validate.txt`,
};

export class AdminAboutAPI extends BaseAPI {
  async about() {
    return await this.requests.get<AdminAboutInfo>(routes.about);
  }

  async statistics() {
    return await this.requests.get(routes.aboutStatistics);
  }

  async checkApp() {
    return await this.requests.get<CheckAppConfig>(routes.check);
  }

  async checkDocker() {
    return await this.requests.get<DockerVolumeText>(routes.docker);
  }

  async getDockerValidateFileContents() {
    return await this.requests.get<string>(routes.validationFile);
  }
}
