import { BaseAPI } from "~/api/_base";

const prefix = "/api";

export class OcrAPI extends BaseAPI {

  async tsv(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return await this.requests.post(`${prefix}/ocr/tsv`, formData);
  }

}
