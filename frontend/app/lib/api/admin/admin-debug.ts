import { BaseAPI } from "../base/base-clients";
import type { DebugResponse } from "~/lib/api/types/admin";

const prefix = "/api";

const routes = {
  openai: providerId => `${prefix}/admin/debug/openai/${providerId}`,
};

export class AdminDebugAPI extends BaseAPI {
  async debugOpenAI(providerId: string, fileObject: Blob | File | undefined = undefined, fileName = "") {
    let formData: FormData | null = null;
    if (fileObject) {
      formData = new FormData();
      formData.append("image", fileObject);
      formData.append("extension", fileName.split(".").pop() ?? "");
    }

    return await this.requests.post<DebugResponse>(routes.openai(providerId), formData);
  }
}
