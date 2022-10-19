import { BaseAPI } from "../base/base-clients";

const prefix = "/api";

export class OcrAPI extends BaseAPI {
  // Currently unused in favor for the endpoint using asset names
  async fileToTsv(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return await this.requests.post(`${prefix}/ocr/file-to-tsv`, formData);
  }

  async assetToTsv(recipeSlug: string, assetName: string) {
    return await this.requests.post(`${prefix}/ocr/asset-to-tsv`, { recipeSlug, assetName });
  }
}
