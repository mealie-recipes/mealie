import { BaseAPI } from "../base/base-clients";

export class UploadFile extends BaseAPI {
  file(url: string, fileObject: any) {
    return this.requests.post<string>(url, fileObject);
  }
}
